import React from "react";
import { Composition, Folder } from "remotion";
import {
  COMPOSITION_REGISTRY,
  type CompositionRegistryEntry,
} from "./compositions";

export { calculateDocumentaryMetadata, calculateMetadata } from "./compositions";

const compositionFolders = Array.from(
  new Set(COMPOSITION_REGISTRY.map((definition) => definition.folder)),
);

const renderRegistryEntry = (definition: CompositionRegistryEntry): React.ReactElement => {
  switch (definition.id) {
    case "Editorial":
      return (
        <Composition
          id={definition.id}
          component={definition.component}
          defaultProps={definition.defaultProps}
          {...definition.metadata}
        />
      );
    case "Documentary":
      return (
        <Composition
          id={definition.id}
          component={definition.component}
          defaultProps={definition.defaultProps}
          {...definition.metadata}
        />
      );
    case "EditorialMotion":
      return (
        <Composition
          id={definition.id}
          component={definition.component}
          defaultProps={definition.defaultProps}
          {...definition.metadata}
        />
      );
    case "FinanceSketchbookProof":
      return (
        <Composition
          id={definition.id}
          component={definition.component}
          defaultProps={definition.defaultProps}
          {...definition.metadata}
        />
      );
    case "FinanceStealthWealthProof":
      return (
        <Composition
          id={definition.id}
          component={definition.component}
          defaultProps={definition.defaultProps}
          {...definition.metadata}
        />
      );
    case "Finance2DStickProof":
      return (
        <Composition
          id={definition.id}
          component={definition.component}
          defaultProps={definition.defaultProps}
          {...definition.metadata}
        />
      );
    case "ProductionEvidence":
      return (
        <Composition
          id={definition.id}
          component={definition.component}
          defaultProps={definition.defaultProps}
          {...definition.metadata}
        />
      );
    default:
      throw new Error(`Unknown composition: ${String(definition)}`);
  }
};

export const RemotionRoot: React.FC = () => (
  <>
    {compositionFolders.map((folder) => (
      <Folder key={folder} name={folder}>
        {COMPOSITION_REGISTRY
          .filter((definition) => definition.folder === folder)
          .map(renderRegistryEntry)}
      </Folder>
    ))}
  </>
);
