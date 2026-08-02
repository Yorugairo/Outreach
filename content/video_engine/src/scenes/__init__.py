"""Importable Manim scene library for the video engine."""

from .base import MANIM_AVAILABLE, ThemedScene, aspect_for_layout
from .bjj_action import BJJActionScene
from .combat_science import (
    COMPOSITION_FUNCTION_NAMES,
    COMPOSITION_FUNCTIONS,
    CombatScienceScene,
)
from .documentary import DocumentaryScene
from .joint_leverage import JointLeverageScene
from .map_network import MapNetworkScene
from .stick_figure import StickFigureScene
from .title_card import TitleConceptCard


SCENE_CLASSES = {
    "BJJActionScene": BJJActionScene,
    "CombatScienceScene": CombatScienceScene,
    "StickFigureScene": StickFigureScene,
    "TitleConceptCard": TitleConceptCard,
    "JointLeverageScene": JointLeverageScene,
    "MapNetworkScene": MapNetworkScene,
    "DocumentaryScene": DocumentaryScene,
}


def scene_class(name: str):
    """Resolve a registry class name without exposing dynamic imports."""

    try:
        return SCENE_CLASSES[name]
    except KeyError as exc:
        raise KeyError(f"unknown scene class: {name}") from exc


__all__ = [
    "MANIM_AVAILABLE",
    "BJJActionScene",
    "CombatScienceScene",
    "COMPOSITION_FUNCTION_NAMES",
    "COMPOSITION_FUNCTIONS",
    "SCENE_CLASSES",
    "ThemedScene",
    "JointLeverageScene",
    "MapNetworkScene",
    "DocumentaryScene",
    "StickFigureScene",
    "TitleConceptCard",
    "aspect_for_layout",
    "scene_class",
]
