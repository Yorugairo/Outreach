import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { describe, test } from "vitest";
import { EditorialComposition } from "../Editorial";
import { EditorialMotionComposition, defaultEditorialMotionProps } from "../EditorialMotion";
import { DocumentaryComposition } from "../Documentary";
import {
  COMPOSITION_REGISTRY,
  REMOTION_VERSION,
} from "../compositions";
import { Finance2DStickProof } from "../Finance2DStickProof";
import { FinanceSketchbookProof } from "../FinanceSketchbookProof";
import { FinanceStealthWealthProof } from "../FinanceStealthWealthProof";
import { ProductionEvidenceComposition } from "../ProductionEvidenceComposition";
import { ProductionTimelineComposition } from "../ProductionTimelineComposition";
import { KenBurnsEffectProof } from "../KenBurnsEffectProof";
import { TransitionEvidence60sProof } from "../TransitionEvidence60sProof";

const editorRoot = new URL("../../", import.meta.url);

describe("composition registry", () => {
  test("preserves all composition IDs and component contracts", () => {
    assert.deepEqual(
      COMPOSITION_REGISTRY.map((definition) => definition.id),
      [
        "Editorial",
        "Documentary",
        "EditorialMotion",
        "FinanceSketchbookProof",
        "FinanceStealthWealthProof",
        "Finance2DStickProof",
        "ProductionEvidence",
        "ProductionTimeline",
        "KenBurnsEffectProof",
        "TransitionEvidence60sProof",
      ],
    );
    assert.equal(new Set(COMPOSITION_REGISTRY.map((definition) => definition.id)).size, 10);

    const components = new Map(COMPOSITION_REGISTRY.map((definition) => [definition.id, definition.component]));
    assert.equal(components.get("Editorial"), EditorialComposition);
    assert.equal(components.get("Documentary"), DocumentaryComposition);
    assert.equal(components.get("EditorialMotion"), EditorialMotionComposition);
    assert.equal(components.get("FinanceSketchbookProof"), FinanceSketchbookProof);
    assert.equal(components.get("FinanceStealthWealthProof"), FinanceStealthWealthProof);
    assert.equal(components.get("Finance2DStickProof"), Finance2DStickProof);
    assert.equal(components.get("ProductionEvidence"), ProductionEvidenceComposition);
    assert.equal(components.get("ProductionTimeline"), ProductionTimelineComposition);
    assert.equal(components.get("KenBurnsEffectProof"), KenBurnsEffectProof);
    assert.equal(components.get("TransitionEvidence60sProof"), TransitionEvidence60sProof);
  });

  test("defaults are JSON-safe and folders are deterministic", () => {
    assert.deepEqual(
      COMPOSITION_REGISTRY.map((definition) => definition.folder),
      ["Editorial", "Documentary", "Editorial", "Finance", "Finance", "Finance", "Console", "Console", "Console", "Console"],
    );

    for (const definition of COMPOSITION_REGISTRY) {
      const encoded = JSON.stringify(definition.defaultProps);
      assert.equal(typeof encoded, "string");
      assert.deepEqual(JSON.parse(encoded), definition.defaultProps);
      assert.ok(definition.metadata.durationInFrames > 0);
      assert.ok(definition.metadata.fps > 0);
      assert.ok(definition.metadata.width > 0);
      assert.ok(definition.metadata.height > 0);
    }

    const editorialMotion = COMPOSITION_REGISTRY.find(({ id }) => id === "EditorialMotion");
    assert.ok(editorialMotion);
    assert.deepEqual(editorialMotion.defaultProps, defaultEditorialMotionProps);
  });

  test("the editor package and lockfile keep exact Remotion parity", () => {
    const packageJson = JSON.parse(readFileSync(new URL("package.json", editorRoot), "utf8")) as {
      dependencies: Record<string, string>;
      devDependencies: Record<string, string>;
    };
    const lockfile = JSON.parse(readFileSync(new URL("package-lock.json", editorRoot), "utf8")) as {
      packages: Record<string, { version?: string }>;
    };
    const packageVersions = {
      ...packageJson.dependencies,
      ...packageJson.devDependencies,
    };
    const remotionPackages = Object.keys(packageVersions).filter((name) => name === "remotion" || name.startsWith("@remotion/"));

    for (const packageName of remotionPackages) {
      assert.equal(packageVersions[packageName], REMOTION_VERSION, `${packageName} package version`);
      const lockEntry = lockfile.packages[`node_modules/${packageName}`];
      assert.ok(lockEntry, `${packageName} lock entry`);
      assert.equal(lockEntry.version, REMOTION_VERSION, `${packageName} lock version`);
    }
  });
});
