"""Helpers for normalising raw CAN-bus log lines before regex parsing."""

from __future__ import annotations

import re


# Keep ordinary whitespace for the next step, but remove non-printing control
# characters which must not become part of a CAN frame field.
_NON_PRINTING_CONTROL_CHARACTERS = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]")
_WHITESPACE_RUN = re.compile(r"\s+")


def sanitize_log_line(raw_line: str) -> str:
    """Return a canonical one-line representation of a raw log record.

    The function removes non-printing control characters, trims leading and
    trailing whitespace and converts runs of spaces or tabs into one space.
    Delimiters and the hexadecimal payload itself are deliberately preserved
    for the regular expression in :mod:`log_parser`.
    """

    without_controls = _NON_PRINTING_CONTROL_CHARACTERS.sub("", raw_line)
    return _WHITESPACE_RUN.sub(" ", without_controls).strip()
