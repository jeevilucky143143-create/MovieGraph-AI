"""UI module for MovieGraph AI implementing the Stitch Pastel Design System."""

from ui.stitch_theme import get_stitch_css
from ui.components import (
    render_navbar,
    render_hero_header,
    render_answer_card,
    render_recommendation_card,
    render_graph_explorer_view,
    render_pipeline_architecture,
)

__all__ = [
    "get_stitch_css",
    "render_navbar",
    "render_hero_header",
    "render_answer_card",
    "render_recommendation_card",
    "render_graph_explorer_view",
    "render_pipeline_architecture",
]
