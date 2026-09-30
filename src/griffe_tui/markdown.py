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

"""Render Griffe objects to Markdown."""

from __future__ import annotations

from typing import TYPE_CHECKING

from griffe2md import prepare_context, prepare_env

if TYPE_CHECKING:
    from griffe import Object


def to_markdown(obj: Object) -> str:
    """Render a Griffe object to Markdown."""
    env = prepare_env()
    context = prepare_context(obj)
    context["heading_level"] = 1
    context["config"]["show_submodules"] = False
    return str(env.get_template(f"{obj.kind.value}.md.jinja").render(**context))
