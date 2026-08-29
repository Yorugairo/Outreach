import type {EditorComponentCatalog, Health, RevisionValidation, Snapshot, SnapshotV2} from './types';

type Envelope<T> = {data?: T; ok?: boolean; error?: {message?: string}};

async function read<T>(url: string): Promise<T> {
  const response = await fetch(url, {headers: {Accept: 'application/json'}});
  const body = (await response.json()) as T | Envelope<T>;
  if (!response.ok) {
    const envelope = body as Envelope<T>;
    throw new Error(envelope.error?.message ?? `Request failed (${response.status})`);
  }
  return (body as Envelope<T>).data ?? (body as T);
}

async function write<T>(url: string, payload: unknown): Promise<T> {
  const response = await fetch(url, {
    method: 'POST',
    headers: {Accept: 'application/json', 'Content-Type': 'application/json'},
    body: JSON.stringify(payload),
  });
  const body = (await response.json()) as T | Envelope<T>;
  if (!response.ok) {
    const envelope = body as Envelope<T>;
    throw new Error(envelope.error?.message ?? `Request failed (${response.status})`);
  }
  return (body as Envelope<T>).data ?? (body as T);
}

export const getSnapshot = () => read<Snapshot>('/api/snapshot');
export const getEditorSnapshot = () => read<SnapshotV2>('/api/editor/snapshot');
export const getComponentCatalog = () => read<EditorComponentCatalog>('/api/editor/components');
export const getEditorialRevisions = () => read<Array<Record<string, unknown>>>('/api/editor/revisions');
export const validateEditorialRevision = (revision: unknown) => write<RevisionValidation>('/api/editor/revisions/validate', revision);
export const saveEditorialRevision = (revision: unknown) => write<Record<string, unknown>>('/api/editor/revisions', revision);
export const getHealth = () => read<Health>('/api/health');
export const mediaUrl = (assetId: string) => `/media/${encodeURIComponent(assetId)}`;
