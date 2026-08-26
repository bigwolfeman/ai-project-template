"""Load a restricted YAML subset with the standard library. No PyYAML."""

from __future__ import annotations

import re
from typing import Any

_INT = re.compile(r"^-?[0-9]+$")
_FLOAT = re.compile(r"^-?[0-9]+\.[0-9]+$")
_KEY = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*$")


class YamlError(ValueError):
    """Invalid restricted YAML."""


def load_yaml(text: str, *, source: str = "<yaml>") -> Any:
    rows: list[tuple[int, int, str]] = []
    for lineno, raw in enumerate(text.splitlines(), 1):
        if "\t" in raw:
            raise YamlError(f"{source}:{lineno}: tabs are not allowed")
        line = _strip_comment(raw)
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        rows.append((lineno, indent, line.strip()))
    if not rows:
        raise YamlError(f"{source}: document is empty")
    value, next_i = _parse_block(rows, 0, rows[0][1], source)
    if next_i != len(rows):
        lineno = rows[next_i][0]
        raise YamlError(f"{source}:{lineno}: unexpected content")
    return value


def _strip_comment(line: str) -> str:
    in_single = False
    in_double = False
    for i, ch in enumerate(line):
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == "#" and not in_single and not in_double:
            return line[:i].rstrip()
    return line.rstrip()


def _parse_block(
    rows: list[tuple[int, int, str]], i: int, min_indent: int, source: str
) -> tuple[Any, int]:
    lineno, indent, content = rows[i]
    if indent < min_indent:
        raise YamlError(f"{source}:{lineno}: invalid indentation")
    if content == "-" or content.startswith("- "):
        return _parse_seq(rows, i, indent, source)
    return _parse_map(rows, i, indent, source)


def _parse_map(
    rows: list[tuple[int, int, str]], i: int, indent: int, source: str
) -> tuple[dict[str, Any], int]:
    out: dict[str, Any] = {}
    while i < len(rows):
        lineno, ind, content = rows[i]
        if ind < indent:
            break
        if ind > indent:
            raise YamlError(f"{source}:{lineno}: invalid indentation")
        if content == "-" or content.startswith("- "):
            raise YamlError(f"{source}:{lineno}: expected mapping key")
        key, raw_val = _split_kv(content, source, lineno)
        if key in out:
            raise YamlError(f"{source}:{lineno}: duplicate key {key!r}")
        i += 1
        if raw_val is None:
            if i < len(rows) and rows[i][1] > indent:
                out[key], i = _parse_block(rows, i, rows[i][1], source)
            else:
                out[key] = None
        else:
            out[key] = _parse_scalar(raw_val, source=source, lineno=lineno)
    return out, i


def _parse_seq(
    rows: list[tuple[int, int, str]], i: int, indent: int, source: str
) -> tuple[list[Any], int]:
    out: list[Any] = []
    while i < len(rows):
        lineno, ind, content = rows[i]
        if ind < indent:
            break
        if ind > indent:
            raise YamlError(f"{source}:{lineno}: invalid indentation")
        if not (content == "-" or content.startswith("- ")):
            raise YamlError(f"{source}:{lineno}: expected sequence item")
        item_text = "" if content == "-" else content[2:].strip()
        i += 1
        if not item_text:
            if i < len(rows) and rows[i][1] > indent:
                val, i = _parse_block(rows, i, rows[i][1], source)
            else:
                val = None
        elif _looks_like_key(item_text):
            val, i = _parse_map_item(rows, i, indent, item_text, lineno, source)
        else:
            val = _parse_scalar(item_text, source=source, lineno=lineno)
        out.append(val)
    return out, i


def _parse_map_item(
    rows: list[tuple[int, int, str]],
    i: int,
    dash_indent: int,
    first_line: str,
    first_lineno: int,
    source: str,
) -> tuple[dict[str, Any], int]:
    mapping: dict[str, Any] = {}
    key, raw_val = _split_kv(first_line, source, first_lineno)
    mapping[key] = _value_or_nested(rows, i, dash_indent, raw_val, source)
    if raw_val is None and i < len(rows) and rows[i][1] > dash_indent:
        mapping[key], i = _parse_block(rows, i, rows[i][1], source)
    while i < len(rows):
        lineno, ind, content = rows[i]
        if ind <= dash_indent:
            break
        if content == "-" or content.startswith("- "):
            break
        key, raw_val = _split_kv(content, source, lineno)
        if key in mapping:
            raise YamlError(f"{source}:{lineno}: duplicate key {key!r}")
        i += 1
        if raw_val is None:
            if i < len(rows) and rows[i][1] > ind:
                mapping[key], i = _parse_block(rows, i, rows[i][1], source)
            else:
                mapping[key] = None
        else:
            mapping[key] = _parse_scalar(raw_val, source=source, lineno=lineno)
    return mapping, i


def _value_or_nested(
    rows: list[tuple[int, int, str]],
    i: int,
    dash_indent: int,
    raw_val: str | None,
    source: str,
) -> Any:
    if raw_val is not None:
        lineno = rows[i - 1][0] if i else 1
        return _parse_scalar(raw_val, source=source, lineno=lineno)
    if i < len(rows) and rows[i][1] > dash_indent:
        return None
    return None


def _looks_like_key(text: str) -> bool:
    if text.endswith(":"):
        return _KEY.match(text[:-1].strip()) is not None
    if ": " not in text:
        return False
    return _KEY.match(text.split(": ", 1)[0].strip()) is not None


def _split_kv(line: str, source: str, lineno: int) -> tuple[str, str | None]:
    if line.endswith(":") and not line.endswith(": "):
        key = line[:-1].strip()
        if _KEY.match(key) is None:
            raise YamlError(f"{source}:{lineno}: invalid key {key!r}")
        return key, None
    if ": " not in line:
        raise YamlError(f"{source}:{lineno}: expected 'key: value'")
    key, value = line.split(": ", 1)
    key = key.strip()
    if _KEY.match(key) is None:
        raise YamlError(f"{source}:{lineno}: invalid key {key!r}")
    return key, value.strip()


def _parse_scalar(raw: str, *, source: str, lineno: int) -> Any:
    if raw == "[]":
        return []
    if raw == "{}":
        return {}
    if raw in ("null", "~"):
        return None
    if raw == "true":
        return True
    if raw == "false":
        return False
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "\"'":
        return raw[1:-1]
    if _INT.fullmatch(raw):
        return int(raw)
    if _FLOAT.fullmatch(raw):
        return float(raw)
    if raw == "" or raw is None:
        raise YamlError(f"{source}:{lineno}: empty scalar")
    return raw
