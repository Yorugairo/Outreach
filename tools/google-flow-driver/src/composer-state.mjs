import {assertComposerState} from './composer-guard.mjs';

/** Read-only snapshot of the observed September 2026 Flow composer.
 * No browser connection, UI mutation, or submission is performed here.
 */
export function inspectComposerDocument(doc = document) {
  const visible = (node) => {
    if (!node) return false;
    const rect = node.getBoundingClientRect();
    const style = doc.defaultView.getComputedStyle(node);
    return rect.width > 0 && rect.height > 0 && style.display !== 'none'
      && style.visibility !== 'hidden';
  };
  const text = (node) => (node?.textContent || '').replace(/\s+/g, ' ').trim();
  // Strip signed query parameters; image identity is carried by the path.
  const thumbnailKey = (img) => {
    if (!img?.getAttribute('src')) return null;
    try {
      const url = new URL(img.getAttribute('src'), doc.baseURI);
      return url.protocol === 'https:' ? `${url.origin}${url.pathname}` : null;
    } catch { return null; }
  };
  const roots = [...doc.querySelectorAll('flow-prompt-box')];
  const root = roots.length === 1 ? roots[0] : null;
  const editors = root ? [...root.querySelectorAll('.ProseMirror')] : [];
  const editor = editors.length === 1 ? editors[0] : null;
  const inlineChips = editor ? [...editor.querySelectorAll('.mention-chip, [data-reference-type]')].map((chip) => ({
    text: text(chip),
    referenceType: chip.getAttribute('data-reference-type'),
    entityId: chip.getAttribute('data-entity-id'),
    mentionId: chip.getAttribute('data-mention-id'),
  })) : [];
  const trayNodes = root ? [...root.querySelectorAll('button.chip-container')] : [];
  const trayChips = trayNodes.map((chip) => {
    const img = chip.querySelector('img');
    const key = thumbnailKey(img);
    const badge = text(chip.querySelector('mat-icon.type-badge'));
    const isCharacter = badge === 'accessibility_new' || img?.alt === 'Character ingredient image';
    const providerId = key?.match(/^https:\/\/flow-content\.google\/image\/([a-f0-9-]+)$/i)?.[1] || null;
    return {
      isCharacter, providerId, thumbnailKey: key,
      imgAlt: img?.alt || null, typeBadge: badge || null,
      visible: visible(chip),
    };
  });
  const contextNodes = root ? [...root.querySelectorAll(
    'button.empty-chip, .start-frame, .end-frame, [class*="start-frame"], [class*="edit-context"], flow-frame-picker-chip'
  )].filter((node) => !node.matches('button[type="submit"], .generate-icon-button')) : [];
  const contextChips = contextNodes.map((node) => ({
    tagName: node.tagName.toLowerCase(), text: text(node),
    ariaLabel: node.getAttribute('aria-label'),
  }));
  // An image outside the known ingredient tray is not silently discarded.
  for (const img of root?.querySelectorAll('img') || []) {
    if (!trayNodes.some((node) => node.contains(img))) {
      contextChips.push({tagName: 'img', unknown: true, thumbnailKey: thumbnailKey(img)});
    }
  }
  const pendingOverlays = [...doc.querySelectorAll('.cdk-overlay-pane, [role="dialog"], [role="listbox"]')]
    .filter(visible).map((node) => ({role: node.getAttribute('role') || 'overlay'}));
  return {
    composerRoot: {selector: 'flow-prompt-box', count: roots.length, visible: visible(root)},
    editor: {selector: 'flow-prompt-box .ProseMirror', count: editors.length, visible: visible(editor), text: text(editor), inlineChipsCount: inlineChips.length, inlineChips},
    tray: {trayElementsCount: trayChips.length, trayChips},
    contextChips, pendingOverlaysCount: pendingOverlays.length, pendingOverlays,
    // Identity must come from a separate observed picker-to-tray mapping,
    // never from index, thumbnail count, or a guessed character name.
    entityTrayBindings: [],
  };
}

export async function captureComposerState(page) {
  return page.evaluate(inspectComposerDocument);
}

/** Require actual picker-to-tray identity evidence supplied by the caller.
 * This checks state only; the caller retains authority for any later submit.
 */
export async function assertLiveComposerState(page, expected, entityTrayBindings = [], options) {
  const snapshot = await captureComposerState(page);
  snapshot.entityTrayBindings = entityTrayBindings;
  assertComposerState(snapshot, expected, options);
  return snapshot;
}
