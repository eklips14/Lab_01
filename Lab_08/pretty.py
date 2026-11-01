"""Текстове представлення JSON-дерева (ЛР8, варіант 9)."""

import json
from typing import assert_never

from model import JSON, JArray, JBool, JNull, JNumber, JObject, JString


def render(node: JSON) -> str:
    """Компактний JSON-текст."""
    match node:
        case JNull():
            return "null"
        case JBool(value=b):
            return "true" if b else "false"
        case JNumber(value=n):
            return json.dumps(n)
        case JString(value=s):
            return json.dumps(s, ensure_ascii=False)
        case JArray(items=items):
            return "[" + ",".join(render(item) for item in items) + "]"
        case JObject(fields=fields):
            pairs = (
                f"{json.dumps(k, ensure_ascii=False)}:{render(v)}" for k, v in fields
            )
            return "{" + ",".join(pairs) + "}"
        case _:
            assert_never(node)


def pretty(node: JSON, indent: int = 2, level: int = 0) -> str:
    """Багаторядковий JSON-текст з відступами."""
    pad, inner = " " * (indent * level), " " * (indent * (level + 1))
    match node:
        case JArray(items=items) if items:
            lines = (inner + pretty(item, indent, level + 1) for item in items)
            return "[\n" + ",\n".join(lines) + "\n" + pad + "]"
        case JObject(fields=fields) if fields:
            lines = (
                f"{inner}{json.dumps(k, ensure_ascii=False)}: "
                f"{pretty(v, indent, level + 1)}"
                for k, v in fields
            )
            return "{\n" + ",\n".join(lines) + "\n" + pad + "}"
        case _:
            return render(node)


def tree(node: JSON, label: str = "root", level: int = 0) -> str:
    """Структура дерева з типами вузлів, по одному вузлу в рядку."""
    prefix = "  " * level
    match node:
        case JArray(items=items):
            head = f"{prefix}{label}: array[{len(items)}]"
            rows = (tree(item, f"[{i}]", level + 1) for i, item in enumerate(items))
            return "\n".join((head, *rows))
        case JObject(fields=fields):
            head = f"{prefix}{label}: object{{{len(fields)}}}"
            rows = (tree(value, key, level + 1) for key, value in fields)
            return "\n".join((head, *rows))
        case _:
            return f"{prefix}{label}: {render(node)}"
