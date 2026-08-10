import {useEffect, useMemo, useState} from 'react';
import {getHealth, getSnapshot} from './api';
import type {Health, Snapshot} from './types';

export function useConsoleData() {
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null);
  const [health, setHealth] = useState<Health | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let alive = true;
    Promise.all([getSnapshot(), getHealth()])
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
