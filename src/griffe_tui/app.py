# SPDX-License-Identifier: ISC
#
# ISC License
#
# Copyright (c) 2023, Timothée Mazzucotelli and contributors
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

"""Definition of the Textual app application."""

from __future__ import annotations

import builtins
import logging
from importlib.metadata import packages_distributions
from pathlib import Path
from typing import TYPE_CHECKING

from griffe import GriffeLoader, Parser
from textual import on
from textual.app import App, ComposeResult, CSSPathType
from textual.widgets import Footer, Header, Input, Markdown, MarkdownViewer

from griffe_tui.markdown import to_markdown

if TYPE_CHECKING:
    from collections.abc import Callable

    from markdown_it import MarkdownIt
    from textual.driver import Driver


logger = logging.getLogger(__name__)

WELCOME = """
# Welcome

To view documentation for a package, module, class,
or any other documented object, try typing its Python path
in the search bar at the top.

By *Python path*, we mean for example `package.module.Class`
or `package.function`.

Below, we list every module available in the current environment.
Try clicking on one of them to show its documentation.

- {modules}
""".format(
    modules="\n- ".join(
        f"[{mod}](#{mod})" for mod in sorted(packages_distributions().keys()) if not mod.startswith("_")
    ),
)


builtin_types = set(vars(builtins))


def _to_markdown(loader: GriffeLoader, path: str) -> str:
    if path in builtin_types:
        path = f"builtins.{path}"
    try:
        obj = loader.modules_collection[path]
    except KeyError:
        loader.load(path.split(".", 1)[0])
        loader.resolve_aliases(external=True, implicit=False)
        obj = loader.modules_collection[path]
    return to_markdown(obj)


class GriffeMarkdownViewer(MarkdownViewer):
    """A Markdown viewer with custom logic for links."""

    def __init__(  # noqa: D107
        self,
        markdown: str | None = None,
        *,
        show_table_of_contents: bool = True,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
        parser_factory: Callable[[], MarkdownIt] | None = None,
        griffe_loader: GriffeLoader,
    ) -> None:
        super().__init__(
            markdown,
            show_table_of_contents=show_table_of_contents,
            name=name,
            id=id,
            classes=classes,
            parser_factory=parser_factory,
            open_links=False,
        )
        self.griffe_loader = griffe_loader

    async def _on_markdown_link_clicked(self, message: Markdown.LinkClicked) -> None:
        message.prevent_default()
        message.stop()
        anchor = message.href
        if anchor.startswith("#"):
            # Slugify the anchor to match Textual slugs.
            if not self.document.goto_anchor(anchor.lstrip("#").replace(".", "").lower()):
                try:
                    # Anchor not on the page: it's another object, load it and render it.
                    markdown = _to_markdown(self.griffe_loader, anchor.lstrip("#"))
                except Exception:
                    logger.exception(f"Couldn't load {anchor} as Markdown")
                else:
                    await self.document.update(markdown)
                    self.scroll_home(animate=False)
        elif anchor.startswith(("https://", "http://")):
            self.app.open_url(anchor)
        else:
            await self.go(anchor)


class GriffeTUIApp(App):
    """A Textual app to visualize docs collected by Griffe."""

    CSS_PATH = Path(__file__).parent / "tcss" / "griffe_tui.tcss"
    BINDINGS = [  # noqa: RUF012
        ("d", "toggle_dark", "Toggle dark mode"),
    ]

    def __init__(  # noqa: D107
        self,
        driver_class: type[Driver] | None = None,
        css_path: CSSPathType | None = None,
        watch_css: bool = False,  # noqa: FBT001,FBT002
        *,
        griffe_loader: GriffeLoader | None = None,
    ) -> None:
        super().__init__(driver_class, css_path, watch_css)
        if griffe_loader is None:
            griffe_loader = GriffeLoader(docstring_parser=Parser.google)
        self.griffe_loader = griffe_loader

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Input(placeholder="Enter a Python object path...")
        yield GriffeMarkdownViewer(WELCOME, griffe_loader=self.griffe_loader)
        yield Footer()

    @on(Input.Submitted)
    async def update_view(self, event: Input.Submitted) -> None:
        """Update the Markdown view."""
        try:
            markdown = _to_markdown(self.griffe_loader, event.value)
        except Exception:
            logger.exception(f"Couldn't load {event.value} as Markdown")
        else:
            viewer = self.query_one(GriffeMarkdownViewer)
            await viewer.document.update(markdown)
            viewer.scroll_home(animate=False)
