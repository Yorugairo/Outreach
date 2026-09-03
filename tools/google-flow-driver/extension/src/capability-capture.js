export const FLOW_CAPABILITY_CAPTURE_VERSION = 'flow-capability-capture.v1';

export class CapabilityCaptureError extends Error {
  constructor(code, message = code) {
    super(message);
    this.name = 'CapabilityCaptureError';
    this.code = code;
  }
}

function sorted(value) {
  if (Array.isArray(value)) return value.map(sorted);
  if (value && typeof value === 'object') {
    return Object.fromEntries(Object.keys(value).sort().map((key) => [key, sorted(value[key])]));
  }
  return value;
}

async function sha256(value) {
  const bytes = new TextEncoder().encode(JSON.stringify(sorted(value)));
  const digest = await globalThis.crypto.subtle.digest('SHA-256', bytes);
  return [...new Uint8Array(digest)].map((byte) => byte.toString(16).padStart(2, '0')).join('');
}

function required(value, code) {
  const normalized = value == null ? '' : String(value).trim();
  if (!normalized) throw new CapabilityCaptureError(code);
  return normalized;
}

function integer(value, fallback = null) {
  if (Number.isInteger(value)) return value;
  const match = String(value ?? '').match(/\d+/);
  return match ? Number(match[0]) : fallback;
}

function projectIdFromUrl(url) {
  try {
    const parsed = new URL(url);
    const match = parsed.pathname.match(/\/project\/([^/?#]+)/i);
    return match?.[1] ? decodeURIComponent(match[1]) : null;
  } catch {
    return null;
  }
}

function actionFor(mode) {
  const normalized = mode.toLowerCase();
  if (normalized.includes('image')) return 'image_generation';
  if (normalized.includes('video')) return 'video_hook_generation';
  throw new CapabilityCaptureError('unsupported_mode', `Unsupported Flow mode: ${mode}`);
}

function creditFields(credit = {}) {
  if (!credit.known) throw new CapabilityCaptureError('credit_unknown');
  const label = required(credit.observed, 'displayed_credit_label_missing');
  if (credit.zero && credit.cost === 0) {
    return { displayed_credit_label: label, credit_state: 'zero', credits_per_generation: 0 };
  }
  if (credit.paid && Number.isInteger(credit.cost) && credit.cost > 0) {
    return { displayed_credit_label: label, credit_state: 'positive', credits_per_generation: credit.cost };
  }
  throw new CapabilityCaptureError('credit_inconsistent');
}

export async function buildCapabilitySnapshot({
  observation,
  accountMarker,
  operatorConfirmedAccount = false,
  extensionVersion,
  observedAt = new Date(),
  expiresMinutes = 15,
} = {}) {
  if (!observation?.ok || !observation.root?.ok) throw new CapabilityCaptureError('flow_project_not_ready');
  if (observation.settings?.ambiguous || observation.settings?.unexpectedMenuCount > 0) {
    throw new CapabilityCaptureError('settings_ambiguous');
  }
  const projectUrl = required(observation.page?.url, 'project_url_missing');
  if (!/^https:\/\/labs\.google\/fx\//i.test(projectUrl)) throw new CapabilityCaptureError('project_url_invalid');
  const projectId = required(observation.root?.projectId || projectIdFromUrl(projectUrl), 'project_id_missing');
  if (!observation.root?.accountVerified && operatorConfirmedAccount !== true) {
    throw new CapabilityCaptureError('account_not_confirmed');
  }
  const marker = required(accountMarker, 'account_marker_missing');
  const settings = observation.settings?.values || {};
  const mode = required(settings.mode, 'mode_missing');
  const model = required(settings.model, 'model_missing');
  const aspectRatio = required(settings.ratio, 'aspect_ratio_missing');
  if (!['16:9', '4:3', '1:1', '3:4', '9:16'].includes(aspectRatio)) {
    throw new CapabilityCaptureError('aspect_ratio_invalid');
  }
  const quantity = integer(settings.quantity, 1);
  if (!Number.isInteger(quantity) || quantity < 1 || quantity > 4) throw new CapabilityCaptureError('quantity_invalid');
  const action = actionFor(mode);
  const duration = action === 'image_generation' ? null : integer(settings.duration, null);
  if (action !== 'image_generation' && (!Number.isInteger(duration) || duration < 1)) {
    throw new CapabilityCaptureError('duration_missing');
  }
  const observed = observedAt instanceof Date ? observedAt : new Date(observedAt);
  if (Number.isNaN(observed.valueOf())) throw new CapabilityCaptureError('observed_at_invalid');
  const expires = new Date(observed.valueOf() + expiresMinutes * 60 * 1000);
  const stamp = observed.toISOString().replace(/[^0-9]/g, '').toLowerCase();
  const safeProject = projectId.toLowerCase().replace(/[^a-z0-9-]+/g, '-').replace(/^-+|-+$/g, '') || 'project';
  const core = {
    schema_version: 'google_flow_capability_snapshot.v1',
    snapshot_id: `flow-${stamp}-${safeProject}`,
    observed_at: observed.toISOString(),
    expires_at: expires.toISOString(),
    project_url: projectUrl,
    project_id: projectId,
    account: { marker, verified: true },
    extension_version: required(extensionVersion, 'extension_version_missing'),
    selector_version: required(observation.selectorVersion, 'selector_version_missing'),
    offerings: [{
      action,
      model,
      mode,
      aspect_ratio: aspectRatio,
      duration_seconds: duration,
      quantity,
      ...creditFields(observation.credit),
    }],
    review_state: 'operator_confirmed',
    render_eligible: false,
  };
  return Object.freeze({ ...core, artifact_hash: await sha256(core) });
}
