import type {Health, Snapshot} from './types';

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

export const getSnapshot = () => read<Snapshot>('/api/snapshot');
export const getHealth = () => read<Health>('/api/health');
export const mediaUrl = (assetId: string) => `/media/${encodeURIComponent(assetId)}`;
