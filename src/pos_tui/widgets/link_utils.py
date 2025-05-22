from __future__ import annotations

"""Utilities for link visualization across widgets."""

LINK_TYPE_COLORS: dict[str, str] = {
    "references": "blue",
    "evolves-from": "green",
    "inspired-by": "yellow",
    "parent-child": "magenta",
}

LINK_TYPE_ICONS: dict[str, str] = {
    "references": "🔗",
    "evolves-from": "🌱",
    "inspired-by": "💡",
    "parent-child": "🧬",
}


def link_type_color(link_type: str) -> str:
    """Return the color used for a given link type."""
    return LINK_TYPE_COLORS.get(link_type, "white")


def link_type_icon(link_type: str) -> str:
    """Return the icon used for a given link type."""
    return LINK_TYPE_ICONS.get(link_type, "🔗")


def format_link_type(link_type: str) -> str:
    """Return ``link_type`` wrapped in markup with its color."""
    color = link_type_color(link_type)
    return f"[{color}]{link_type}[/{color}]"
