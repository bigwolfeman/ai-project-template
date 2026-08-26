"""JSON Schema Draft 2020-12 subset: required, types, enums, additionalProperties."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from yaml_subset import YamlError, load_yaml

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas"


class SchemaError(ValueError):
    """Instance failed schema validation."""


class SchemaStore:
    def __init__(self, schema_dir: Path = SCHEMA_DIR) -> None:
        self.schema_dir = schema_dir
        self._docs: dict[Path, dict[str, Any]] = {}

    def load(self, path: Path) -> dict[str, Any]:
        resolved = path.resolve()
        if resolved not in self._docs:
            if not resolved.is_file():
                raise SchemaError(f"missing schema file: {resolved}")
            self._docs[resolved] = json.loads(resolved.read_text(encoding="utf-8"))
        return self._docs[resolved]


def format_field(parts: list[str | int]) -> str:
    if not parts:
        return "<root>"
    return ".".join(str(p) for p in parts)


def load_document(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        return load_yaml(text, source=str(path))
    if suffix == ".json":
        return json.loads(text)
    raise SchemaError(f"{path}: unsupported document type {suffix}")


def load_jsonl(path: Path) -> list[Any]:
    events: list[tuple[str, Any]] = []
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            events.append((raw, json.loads(raw)))
        except json.JSONDecodeError as exc:
            raise SchemaError(f"{path}:{lineno}: invalid JSON: {exc.msg}") from exc
    return events


def validate_instance(
    instance: Any,
    schema: dict[str, Any] | bool,
    *,
    source: str,
    schema_path: Path,
    store: SchemaStore | None = None,
) -> list[str]:
    ctx = store or SchemaStore(schema_path.parent)
    errors: list[str] = []
    _validate(instance, schema, [], source, schema_path, ctx, errors)
    return errors


def validate_file(path: Path, schema_path: Path, store: SchemaStore | None = None) -> list[str]:
    ctx = store or SchemaStore(schema_path.parent)
    schema = ctx.load(schema_path)
    try:
        instance = load_document(path)
    except (YamlError, json.JSONDecodeError, SchemaError) as exc:
        return [str(exc)]
    return validate_instance(
        instance, schema, source=str(path), schema_path=schema_path, store=ctx
    )


def _validate(
    instance: Any,
    schema: dict[str, Any] | bool,
    path: list[str | int],
    source: str,
    schema_file: Path,
    store: SchemaStore,
    errors: list[str],
) -> None:
    loc = f"{source}: {format_field(path)}"
    if schema is True:
        return
    if schema is False:
        errors.append(f"{loc}: schema rejects this value")
        return
    if not isinstance(schema, dict):
        errors.append(f"{loc}: invalid schema document")
        return
    if "$ref" in schema:
        ref_schema, ref_file = _resolve_ref(schema["$ref"], schema_file, store)
        _validate(instance, ref_schema, path, source, ref_file, store, errors)
    if "const" in schema and instance != schema["const"]:
        errors.append(f"{loc}: expected const {schema['const']!r}")
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{loc}: {instance!r} is not one of {schema['enum']}")
    declared = schema.get("type")
    if declared is not None:
        types = declared if isinstance(declared, list) else [declared]
        if not any(_type_ok(instance, t) for t in types):
            errors.append(f"{loc}: expected type {declared}, got {_actual_type(instance)}")
            return
    if "allOf" in schema:
        for sub in schema["allOf"]:
            _validate(instance, sub, path, source, schema_file, store, errors)
    if "anyOf" in schema:
        if not _matches_any(instance, schema["anyOf"], path, source, schema_file, store):
            errors.append(f"{loc}: value does not match any allowed schema")
    if "oneOf" in schema:
        hits = sum(
            1
            for sub in schema["oneOf"]
            if _matches_any(instance, [sub], path, source, schema_file, store)
        )
        if hits != 1:
            errors.append(f"{loc}: value must match exactly one schema (matched {hits})")
    if isinstance(instance, dict):
        _validate_object(instance, schema, path, source, schema_file, store, errors)
    if isinstance(instance, list):
        _validate_array(instance, schema, path, source, schema_file, store, errors)
    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(f"{loc}: shorter than minLength {schema['minLength']}")
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            errors.append(f"{loc}: longer than maxLength {schema['maxLength']}")
        if "pattern" in schema and re.fullmatch(schema["pattern"], instance) is None:
            errors.append(f"{loc}: does not match pattern {schema['pattern']}")
    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{loc}: below minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{loc}: above maximum {schema['maximum']}")


def _validate_object(
    instance: dict[str, Any],
    schema: dict[str, Any],
    path: list[str | int],
    source: str,
    schema_file: Path,
    store: SchemaStore,
    errors: list[str],
) -> None:
    loc = f"{source}: {format_field(path)}"
    props = schema.get("properties", {})
    additional = schema.get("additionalProperties", True)
    for req in schema.get("required", []):
        if req not in instance:
            errors.append(f"{loc}: {req}: missing required field")
    for key, value in instance.items():
        child = path + [key]
        if key in props:
            _validate(value, props[key], child, source, schema_file, store, errors)
        elif additional is False:
            errors.append(f"{source}: {format_field(child)}: unknown field")
        elif isinstance(additional, dict):
            _validate(value, additional, child, source, schema_file, store, errors)


def _validate_array(
    instance: list[Any],
    schema: dict[str, Any],
    path: list[str | int],
    source: str,
    schema_file: Path,
    store: SchemaStore,
    errors: list[str],
) -> None:
    loc = f"{source}: {format_field(path)}"
    if "minItems" in schema and len(instance) < schema["minItems"]:
        errors.append(f"{loc}: fewer than minItems {schema['minItems']}")
    if "maxItems" in schema and len(instance) > schema["maxItems"]:
        errors.append(f"{loc}: more than maxItems {schema['maxItems']}")
    item_schema = schema.get("items")
    if item_schema is None:
        return
    for idx, item in enumerate(instance):
        _validate(item, item_schema, path + [idx], source, schema_file, store, errors)


def _matches_any(
    instance: Any,
    schemas: list[Any],
    path: list[str | int],
    source: str,
    schema_file: Path,
    store: SchemaStore,
) -> bool:
    for sub in schemas:
        probe: list[str] = []
        _validate(instance, sub, path, source, schema_file, store, probe)
        if not probe:
            return True
    return False


def _resolve_ref(ref: str, schema_file: Path, store: SchemaStore) -> tuple[Any, Path]:
    doc_ref, _, pointer = ref.partition("#")
    target = schema_file if not doc_ref else (schema_file.parent / doc_ref).resolve()
    node: Any = store.load(target)
    for part in pointer.split("/"):
        if part == "":
            continue
        part = part.replace("~1", "/").replace("~0", "~")
        if not isinstance(node, dict) or part not in node:
            raise SchemaError(f"{schema_file}: unresolved $ref {ref}")
        node = node[part]
    return node, target


def _type_ok(value: Any, declared: str) -> bool:
    if declared == "object":
        return isinstance(value, dict)
    if declared == "array":
        return isinstance(value, list)
    if declared == "string":
        return isinstance(value, str)
    if declared == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if declared == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if declared == "boolean":
        return isinstance(value, bool)
    if declared == "null":
        return value is None
    return False


def _actual_type(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    if isinstance(value, str):
        return "string"
    return type(value).__name__
