"""Render Griffe objects to Markdown."""

from __future__ import annotations

from typing import TYPE_CHECKING

from griffe2md.main import prepare_context, prepare_env

if TYPE_CHECKING:
    from griffe import Object


def to_markdown(obj: Object) -> str:
    """Render a Griffe object to Markdown."""
    env = prepare_env()
    context = prepare_context(obj)
    context["heading_level"] = 1
    context["config"]["show_submodules"] = False
    return str(env.get_template(f"{obj.kind.value}.md.jinja").render(**context))
