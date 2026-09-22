/**
 * Pure, fail-closed validation for the observed Flow composer.
 *
 * This module deliberately knows nothing about Playwright/CDP or submission. A
 * collector supplies one redacted snapshot and the caller supplies the exact
 * reference allow-list it intended to bind. Missing evidence is an error, not
 * an invitation to infer state from counts or labels.
 */

const UNKNOWN = new Set(['', 'unknown', 'null', 'undefined', 'n/a', 'none']);

function isRecord(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function nonEmpty(value) {
  return typeof value === 'string' && value.trim().length > 0;
}

function known(value) {
  return nonEmpty(value) && !UNKNOWN.has(value.trim().toLowerCase());
}

function asList(value, label, errors) {
  if (!Array.isArray(value)) {
    errors.push(`${label} must be an observed array (missing/unknown evidence)`);
    return [];
  }
  return value;
}

function exactReferenceList(expected, errors) {
  const refs = Array.isArray(expected) ? expected : expected?.references;
  if (!Array.isArray(refs)) {
    errors.push('expected references must be an explicit array of {type,id,name}');
    return [];
  }
  const seen = new Set();
  return refs.map((ref, index) => {
    if (!isRecord(ref)) {
      errors.push(`expected reference ${index} is not an object`);
      return { type: '', id: '', name: '' };
    }
    const normalized = {
      type: typeof ref.type === 'string' ? ref.type.trim() : '',
      id: typeof ref.id === 'string' ? ref.id.trim() : '',
      name: typeof ref.name === 'string' ? ref.name.trim() : '',
    };
    if (!['entity', 'media'].includes(normalized.type)) {
      errors.push(`expected reference ${index} has unsupported type ${JSON.stringify(normalized.type)}`);
    }
    if (!known(normalized.id) || !known(normalized.name)) {
      errors.push(`expected reference ${index} requires exact non-empty id and name`);
    }
    const key = `${normalized.type}\u0000${normalized.id}\u0000${normalized.name}`;
    if (seen.has(key)) errors.push(`duplicate expected reference ${normalized.type}:${normalized.id}`);
    seen.add(key);
    return normalized;
  });
}

function assertObservedCountVisibility(node, label, errors) {
  if (!isRecord(node)) {
    errors.push(`${label} observation is missing`);
    return;
  }
  const readable = label === 'composerRoot' ? 'composer root' : label;
  if (node.count !== 1) errors.push(`${label} (${readable}) must represent exactly one active root (count=1)`);
  if (node.visible !== true) errors.push(`${label} (${readable}) must be visibly active (visible=true)`);
  if (!nonEmpty(node.selector)) errors.push(`${label}.selector is missing/unknown`);
}

function chipIdentity(chip, type) {
  if (!isRecord(chip)) return [];
  if (type === 'entity') {
    return [chip.entityId, chip.mentionId].filter(known);
  }
  // New Flow reports media identity in mentionId; older captures sometimes
  // expose providerId/entityId. The exact expected id must match one observed
  // identifier, never merely a filename or count.
  return [chip.mentionId, chip.entityId, chip.providerId, chip.mediaId].filter(known);
}

function chipMatchesReference(chip, ref) {
  if (!isRecord(chip) || chip.referenceType !== ref.type || chip.text !== ref.name) return false;
  if (ref.type === 'entity') {
    // A Character chip has a stable entity id. If Flow exposes both aliases,
    // they must agree; accepting one expected alias beside one stale alias
    // would let a previous character satisfy a count-based check.
    if (chip.entityId !== ref.id) return false;
    return !known(chip.mentionId) || chip.mentionId === ref.id;
  }
  const ids = chipIdentity(chip, 'media');
  return ids.length > 0 && ids.every((id) => id === ref.id);
}

function validateInline(snapshot, refs, errors) {
  const editor = snapshot.editor;
  if (!isRecord(editor)) {
    errors.push('editor observation is missing');
    return;
  }
  assertObservedCountVisibility(editor, 'editor', errors);
  if (!nonEmpty(editor.selector)) errors.push('editor.selector is missing/unknown');
  if (typeof editor.text !== 'string') {
    errors.push('editor.text is missing/unknown');
  } else if (refs.length > 0 && editor.text.trim().length === 0) {
    errors.push('prepared composer editor.text must be non-empty');
  } else if (refs.length === 0 && editor.text !== '') {
    errors.push('zero/reset composer editor.text must be exactly empty');
  }
  const chips = asList(editor.inlineChips, 'editor.inlineChips', errors);
  if (!Number.isInteger(editor.inlineChipsCount)) {
    errors.push('editor.inlineChipsCount is missing/unknown');
  } else if (editor.inlineChipsCount !== chips.length) {
    errors.push(`editor inline chip count mismatch: declared ${editor.inlineChipsCount}, observed ${chips.length}`);
  }
  if (chips.length !== refs.length) {
    errors.push(`inline reference count mismatch: expected ${refs.length}, observed ${chips.length}`);
  }

  const seenIds = new Set();
  const seenKeys = new Set();
  for (const [index, chip] of chips.entries()) {
    if (!isRecord(chip)) {
      errors.push(`inline chip ${index} is not an observed object`);
      continue;
    }
    const type = chip.referenceType;
    if (!['entity', 'media'].includes(type)) {
      errors.push(`inline chip ${index} has unknown reference type ${JSON.stringify(type)}`);
      continue;
    }
    const ids = chipIdentity(chip, type);
    const matching = refs.filter((ref) => chipMatchesReference(chip, ref));
    if (matching.length !== 1) {
      const idText = ids.length ? ids.join(',') : 'unknown';
      errors.push(`inline chip ${index} does not exactly match an expected ${type} identity/name (ids=${idText}, name=${JSON.stringify(chip.text)})`);
      continue;
    }
    const ref = matching[0];
    const key = `${ref.type}\u0000${ref.id}`;
    if (seenKeys.has(key)) errors.push(`duplicate inline reference ${ref.type}:${ref.id}`);
    seenKeys.add(key);
    // entityId and mentionId are two aliases for one chip in the observed
    // Flow DOM; aliases within this chip are not duplicate references. A
    // duplicate is an identity repeated by a *different* chip.
    const chipIds = new Set(ids);
    for (const id of chipIds) {
      if (seenIds.has(`${type}\u0000${id}`)) errors.push(`duplicate inline ${type} identity ${id}`);
    }
    for (const id of chipIds) seenIds.add(`${type}\u0000${id}`);
  }
  for (const ref of refs) {
    if (!seenKeys.has(`${ref.type}\u0000${ref.id}`)) {
      errors.push(`missing inline reference coverage for ${ref.type}:${ref.id}`);
    }
  }
}

function validateEntityBindings(snapshot, entityRefs, errors) {
  const bindings = asList(snapshot.entityTrayBindings, 'entityTrayBindings', errors);
  const expectedIds = new Set(entityRefs.map((ref) => ref.id));
  const byEntity = new Map();
  const thumbnails = new Set();
  for (const [index, binding] of bindings.entries()) {
    if (!isRecord(binding) || !known(binding.entityId) || !known(binding.thumbnailKey)) {
      errors.push(`entityTrayBindings[${index}] lacks separately observed entityId/thumbnailKey evidence`);
      continue;
    }
    if (!expectedIds.has(binding.entityId)) {
      errors.push(`entityTrayBindings contains unexpected entity ${binding.entityId}`);
    }
    if (byEntity.has(binding.entityId)) errors.push(`duplicate entityTrayBindings entry for ${binding.entityId}`);
    byEntity.set(binding.entityId, binding.thumbnailKey);
    if (thumbnails.has(binding.thumbnailKey)) errors.push(`duplicate character thumbnail binding ${binding.thumbnailKey}`);
    thumbnails.add(binding.thumbnailKey);
  }
  if (bindings.length !== entityRefs.length) {
    errors.push(`entity tray binding count mismatch: expected ${entityRefs.length}, observed ${bindings.length}`);
  }
  for (const ref of entityRefs) {
    if (!byEntity.has(ref.id)) errors.push(`missing entity-to-thumbnail evidence for ${ref.id}`);
  }
  return byEntity;
}

function trayIdentity(chip) {
  return [chip?.providerId, chip?.mediaId, chip?.entityId].filter(known);
}

function validateTray(snapshot, refs, errors) {
  if (!isRecord(snapshot.tray)) {
    errors.push('tray observation is missing');
    return;
  }
  const chips = asList(snapshot.tray.trayChips, 'tray.trayChips', errors);
  if (!Number.isInteger(snapshot.tray.trayElementsCount)) {
    errors.push('tray.trayElementsCount is missing/unknown');
  } else if (snapshot.tray.trayElementsCount !== chips.length) {
    errors.push(`tray count mismatch: declared ${snapshot.tray.trayElementsCount}, observed ${chips.length}`);
  }
  if (chips.length !== refs.length) {
    errors.push(`tray item count mismatch: expected ${refs.length}, observed ${chips.length}`);
  }
  const entityRefs = refs.filter((ref) => ref.type === 'entity');
  const mediaRefs = refs.filter((ref) => ref.type === 'media');
  const entityBindings = validateEntityBindings(snapshot, entityRefs, errors);
  const seen = new Set();
  for (const [index, chip] of chips.entries()) {
    if (!isRecord(chip)) {
      errors.push(`tray chip ${index} is not an observed object`);
      continue;
    }
    if (chip.visible !== true) {
      errors.push(`tray chip ${index} visibility is missing/false`);
      continue;
    }
    if (typeof chip.isCharacter !== 'boolean') {
      errors.push(`tray chip ${index} has unknown character/media type`);
      continue;
    }
    if (chip.isCharacter) {
      if (!known(chip.thumbnailKey)) {
        errors.push(`character tray chip ${index} lacks separately evidenced thumbnailKey`);
        continue;
      }
      const matches = entityRefs.filter((ref) => entityBindings.get(ref.id) === chip.thumbnailKey);
      if (matches.length !== 1) {
        errors.push(`character tray chip ${index} has unexpected thumbnail binding ${chip.thumbnailKey}`);
        continue;
      }
      const key = `entity\u0000${matches[0].id}`;
      if (seen.has(key)) errors.push(`duplicate character tray item ${matches[0].id}`);
      seen.add(key);
    } else {
      const ids = trayIdentity(chip);
      const matches = mediaRefs.filter((ref) => ids.length > 0 && ids.every((id) => id === ref.id));
      if (matches.length !== 1) {
        errors.push(`media tray chip ${index} does not exactly match an expected media id (ids=${ids.join(',') || 'unknown'})`);
        continue;
      }
      const key = `media\u0000${matches[0].id}`;
      if (seen.has(key)) errors.push(`duplicate media tray item ${matches[0].id}`);
      seen.add(key);
    }
  }
  for (const ref of refs) {
    if (!seen.has(`${ref.type}\u0000${ref.id}`)) errors.push(`missing tray coverage for ${ref.type}:${ref.id}`);
  }
}

function validateContext(snapshot, errors) {
  const context = asList(snapshot.contextChips, 'contextChips', errors);
  if (context.length > 0) errors.push(`contextChips has ${context.length} pending/unrecognized item(s)`);
  const pending = asList(snapshot.pendingOverlays, 'pendingOverlays', errors);
  if (!Number.isInteger(snapshot.pendingOverlaysCount)) {
    errors.push('pendingOverlaysCount is missing/unknown');
  } else if (snapshot.pendingOverlaysCount !== pending.length) {
    errors.push(`pendingOverlaysCount mismatch: declared ${String(snapshot.pendingOverlaysCount)}, observed ${pending.length}`);
  }
  if (pending.length > 0) errors.push(`pendingOverlays has ${pending.length} pending picker/context item(s)`);
}

/**
 * Validate one observed Flow composer state.
 *
 * `expected` is either an array or `{references: [...]}`. Each reference is
 * exactly `{type: 'entity'|'media', id, name}`. `mode:'zero'` validates the
 * post-reset empty state separately from a prepared composer.
 */
export function validateComposerState(snapshot, expected, { mode = 'prepared' } = {}) {
  const errors = [];
  if (!isRecord(snapshot)) return { ok: false, errors: ['composer snapshot is missing/unknown'] };
  if (!['prepared', 'zero'].includes(mode)) errors.push(`unsupported composer validation mode ${JSON.stringify(mode)}`);
  const refs = exactReferenceList(expected, errors);
  if (mode === 'zero' && refs.length > 0) errors.push('zero/reset mode requires an empty expected reference allow-list');
  if (mode === 'prepared' && refs.length === 0) errors.push('prepared mode requires a non-empty expected reference allow-list');

  assertObservedCountVisibility(snapshot.composerRoot, 'composerRoot', errors);
  validateContext(snapshot, errors);
  validateInline(snapshot, refs, errors);
  validateTray(snapshot, refs, errors);

  if (mode === 'zero') {
    const inlineCount = snapshot.editor?.inlineChipsCount;
    const trayCount = snapshot.tray?.trayElementsCount;
    if (inlineCount !== 0) errors.push(`zero/reset requires inlineChipsCount=0, observed ${String(inlineCount)}`);
    if (trayCount !== 0) errors.push(`zero/reset requires trayElementsCount=0, observed ${String(trayCount)}`);
    if (Array.isArray(snapshot.entityTrayBindings) && snapshot.entityTrayBindings.length !== 0) {
      errors.push('zero/reset requires no entity-to-thumbnail bindings');
    }
  }
  return { ok: errors.length === 0, errors };
}

export function assertComposerState(snapshot, expected, options) {
  const result = validateComposerState(snapshot, expected, options);
  if (!result.ok) throw new Error(`Composer guard failed:\n- ${result.errors.join('\n- ')}`);
  return result;
}
