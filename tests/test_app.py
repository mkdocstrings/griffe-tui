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

"""Tests for the Textual app."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from textual.widgets import Input, Markdown

from griffe_tui import GriffeMarkdownViewer, GriffeTUIApp

if TYPE_CHECKING:
    import pytest


def test_search_renders_document_and_toggles_theme() -> None:
    """Searching for an object updates the viewer without crashing."""

    async def run_app() -> None:
        app = GriffeTUIApp()

        async with app.run_test() as pilot:
            viewer = app.query_one(GriffeMarkdownViewer)
            app.query_one(Input).value = "builtins.int"

            await pilot.press("enter")
            await pilot.pause()

            assert viewer.document.source.lstrip().startswith("# `builtins.int`")

            app.action_toggle_dark()

            assert app.theme == "textual-light"

    asyncio.run(run_app())


def test_object_link_loads_another_document() -> None:
    """A link to a Python object replaces the current document."""

    async def run_app() -> None:
        app = GriffeTUIApp()

        async with app.run_test() as pilot:
            viewer = app.query_one(GriffeMarkdownViewer)

            viewer.document.post_message(Markdown.LinkClicked(viewer.document, "#builtins.int"))
            await pilot.pause()

            assert viewer.document.source.lstrip().startswith("# `builtins.int`")

    asyncio.run(run_app())


def test_web_link_opens_in_browser(monkeypatch: pytest.MonkeyPatch) -> None:
    """A web link opens through Textual instead of being read as a local file."""

    async def run_app() -> None:
        app = GriffeTUIApp()
        opened_urls: list[str] = []
        monkeypatch.setattr(app, "open_url", opened_urls.append)

        async with app.run_test() as pilot:
            viewer = app.query_one(GriffeMarkdownViewer)

            viewer.document.post_message(Markdown.LinkClicked(viewer.document, "https://example.com/docs"))
            await pilot.pause()

            assert opened_urls == ["https://example.com/docs"]

    asyncio.run(run_app())
