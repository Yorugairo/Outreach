import assert from 'node:assert/strict';
import test from 'node:test';
import {
  MediaObservationError,
  createMediaObserver,
  diffMediaSnapshots,
  selectFreshMedia,
  snapshotMedia,
} from '../extension/src/media-observer.js';

const stale = { id: 'stale-1', url: 'https://cdn.example/stale.png', status: 'settled', settled: true };

test('before/after snapshots exclude stale media and require a stable new item', async () => {
  const observer = createMediaObserver({ stabilityPolls: 2, pollIntervalMs: 0 });
  observer.begin({ media: { items: [stale], failures: [] } });
  const snapshots = [
    { media: { items: [stale, { id: 'new-1', requestId: 'item-1', status: 'generating', settled: false }], failures: [] } },
    { media: { items: [stale, { id: 'new-1', requestId: 'item-1', status: 'settled', settled: true, url: 'https://cdn.example/new-1.png' }], failures: [] } },
    { media: { items: [stale, { id: 'new-1', requestId: 'item-1', status: 'settled', settled: true, url: 'https://cdn.example/new-1.png' }], failures: [] } },
  ];
  const result = await observer.waitForStableNewMedia({
    expected: { requestId: 'item-1' },
    getSnapshot: () => snapshots.shift() || snapshots.at(-1),
    timeoutMs: 1000,
  });
  assert.equal(result.item.id, 'new-1');
  assert.equal(result.items.length, 1);
  assert.equal(result.diff.added.length, 1);
  assert.equal(result.diff.added[0].id, 'new-1');
  assert.equal(result.diff.added.some((item) => item.id === 'stale-1'), false);
});

test('the provider/card ID remains stable when Flow fills the URL after insertion', () => {
  const before = snapshotMedia({ media: { items: [{ id: 'existing', status: 'settled', settled: true }], failures: [] } });
  const after = snapshotMedia({ media: { items: [{ id: 'existing', url: 'https://cdn.example/existing.png', status: 'settled', settled: true }], failures: [] } });
  const diff = diffMediaSnapshots(before, after);
  assert.deepEqual(diff.added, []);
  assert.equal(diff.unchanged[0].id, 'existing');
});

test('explicit request association rejects an unbound or different Flow result', () => {
  const before = snapshotMedia({ media: { items: [stale], failures: [] } });
  const after = snapshotMedia({ media: { items: [
    stale,
    { id: 'wrong', requestId: 'other-item', status: 'settled', settled: true, url: 'https://cdn.example/wrong.png' },
    { id: 'right', requestId: 'item-1', status: 'settled', settled: true, url: 'https://cdn.example/right.png' },
  ], failures: [] } });
  const result = selectFreshMedia(before, after, { requestId: 'item-1' });
  assert.equal(result.ok, true);
  assert.deepEqual(result.settled.map((item) => item.id), ['right']);
});

test('serial before/after attribution accepts one fresh settled card when Flow exposes no request ID', () => {
  const before = snapshotMedia({ media: { items: [stale], failures: [] } });
  const after = snapshotMedia({ media: { items: [
    stale,
    { id: 'fresh-unbound', status: 'settled', settled: true, url: 'https://cdn.example/fresh-unbound.png' },
  ], failures: [] } });
  const result = selectFreshMedia(before, after, {});
  assert.equal(result.ok, true);
  assert.deepEqual(result.settled.map((item) => item.id), ['fresh-unbound']);
});

test('generation failures are surfaced before a stale/new item can be accepted', async () => {
  const observer = createMediaObserver({ stabilityPolls: 1, pollIntervalMs: 0 });
  observer.begin({ media: { items: [stale], failures: [] } });
  await assert.rejects(
    observer.waitForStableNewMedia({
      getSnapshot: () => ({ media: { items: [stale], failures: [{ status: 'failed' }] } }),
      timeoutMs: 100,
    }),
    (error) => error instanceof MediaObservationError && error.code === 'generation_failed',
  );
});
