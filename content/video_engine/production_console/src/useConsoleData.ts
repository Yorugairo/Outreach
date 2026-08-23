import {useEffect, useMemo, useState} from 'react';
import {getEditorSnapshot, getHealth} from './api';
import type {Health, SnapshotV2} from './types';

export function useConsoleData() {
  const [snapshot, setSnapshot] = useState<SnapshotV2 | null>(null);
  const [health, setHealth] = useState<Health | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let alive = true;
    Promise.all([getEditorSnapshot(), getHealth()])
      .then(([nextSnapshot, nextHealth]) => {
        if (!alive) return;
        setSnapshot(nextSnapshot);
        setHealth(nextHealth);
      })
      .catch((reason: unknown) => alive && setError(reason instanceof Error ? reason.message : String(reason)))
      .finally(() => alive && setLoading(false));
    return () => { alive = false; };
  }, []);

  return useMemo(() => ({snapshot, health, error, loading}), [snapshot, health, error, loading]);
}
