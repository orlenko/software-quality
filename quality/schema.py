"""Strict validator for our explicitly limited JSON Schema vocabulary."""
from __future__ import annotations

from importlib.resources import files
import re
from typing import Any

from quality_trust import Invalid, parse_json

TYPES = {"object": dict, "array": list, "string": str, "integer": int,
         "boolean": bool, "null": type(None)}
KEYWORDS = {"$schema", "title", "description", "type", "properties", "required",
            "additionalProperties", "items", "enum", "const", "minimum", "maximum",
            "minItems", "maxItems", "minLength", "maxLength", "pattern", "$ref", "$defs"}


def validate(value: Any, rule: dict[str, Any]) -> None:
    if set(rule) - KEYWORDS:
        raise Invalid("unsupported-schema-keyword")
    if "$ref" in rule:
        name, _, fragment = rule["$ref"].partition("#")
        if name not in {"common.json", "config.json", "review-record.json"}:
            raise Invalid("unsupported-schema-reference")
        target = parse_json(files("quality").joinpath("schemas", name).read_bytes())
        for part in fragment.split("/")[1:]:
            target = target[part]
        validate(value, target)
    if "type" in rule and type(value) is not TYPES[rule["type"]]:
        raise Invalid("schema-type")
    if "const" in rule and (type(value) is not type(rule["const"]) or value != rule["const"]):
        raise Invalid("schema-const")
    if "enum" in rule and not any(type(value) is type(item) and value == item for item in rule["enum"]):
        raise Invalid("schema-enum")
    if type(value) is dict:
        props = rule.get("properties", {})
        if not set(rule.get("required", [])) <= set(value):
            raise Invalid("schema-required")
        if rule.get("additionalProperties") is False and set(value) - set(props):
            raise Invalid("schema-unknown-field")
        for key, item in value.items():
            if key in props:
                validate(item, props[key])
    if type(value) in (str, list):
        lower, upper = ("minLength", "maxLength") if type(value) is str else ("minItems", "maxItems")
        if len(value) < rule.get(lower, 0) or len(value) > rule.get(upper, 1000000):
            raise Invalid("schema-size")
    if type(value) is str and "pattern" in rule and re.fullmatch(rule["pattern"], value) is None:
        raise Invalid("schema-pattern")
    if type(value) is int and not rule.get("minimum", value) <= value <= rule.get("maximum", value):
        raise Invalid("schema-range")
    if type(value) is list and "items" in rule:
        for item in value:
            validate(item, rule["items"])


def checked(name: str, value: Any) -> Any:
    rule = parse_json(files("quality").joinpath("schemas", name + ".json").read_bytes())
    validate(value, rule)
    return value
