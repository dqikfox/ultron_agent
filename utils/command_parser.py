"""
Shared command-parsing helpers for ULTRON Agent tools.

Provides generic utilities for extracting the meaningful payload from a
natural-language command string by stripping well-known trigger keywords.
Previously this pattern was duplicated individually in each tool
(``_extract_prompt``, ``_extract_query``, etc.).
"""

from __future__ import annotations

from typing import List, Optional


def extract_after_keyword(
    command: str,
    keywords: List[str],
    *,
    case_sensitive: bool = False,
) -> str:
    """Return the part of *command* that follows the first matched keyword.

    The comparison is performed on a lower-cased copy of *command* so that
    keyword matching is case-insensitive by default.  The original casing of
    the remaining text is preserved when ``case_sensitive=False``.

    Parameters
    ----------
    command:
        The raw command string received by a tool.
    keywords:
        Ordered list of trigger strings.  The first one found (using
        ``str.split``) is used to split the command.
    case_sensitive:
        When *True* the keyword search honours the original casing of
        *command*.

    Returns
    -------
    str
        The text after the matched keyword, stripped of leading/trailing
        whitespace.  If no keyword matches, the original *command* is returned
        unchanged.
    """
    compare = command if case_sensitive else command.lower()

    for keyword in keywords:
        kw = keyword if case_sensitive else keyword.lower()
        if kw in compare:
            # Split on the *original* string at the matched position so we
            # preserve the caller's casing in the remainder.
            idx = compare.find(kw)
            remainder = command[idx + len(kw) :].strip()
            if remainder:
                return remainder

    return command


def strip_leading_keywords(
    command: str,
    prefixes: List[str],
    *,
    case_sensitive: bool = False,
) -> str:
    """Strip a leading prefix keyword from *command*.

    Unlike :func:`extract_after_keyword` (which splits on any occurrence of a
    keyword), this function only removes a prefix that appears *at the start*
    of the command.

    Parameters
    ----------
    command:
        The raw command string received by a tool.
    prefixes:
        Ordered list of prefix strings.  The first one found at the start of
        the command is removed.
    case_sensitive:
        When *True* the prefix search honours the original casing of *command*.

    Returns
    -------
    str
        The command with the leading prefix stripped, or the original command
        if no prefix matched.
    """
    compare = command if case_sensitive else command.lower()

    for prefix in prefixes:
        pfx = prefix if case_sensitive else prefix.lower()
        if compare.startswith(pfx):
            remainder = command[len(pfx) :].strip()
            return remainder if remainder else command

    return command
