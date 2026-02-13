import json
import os
from pathlib import Path

from app.main import app

SNAPSHOT_PATH = Path(__file__).parent / "snapshots" / "openapi_signature.json"


def _param_type(param: dict) -> str:
    schema = param.get("schema", {})
    if "anyOf" in schema:
        types = sorted({item.get("type", "object") for item in schema["anyOf"]})
        return "|".join(types)
    return schema.get("type", "object")


def _build_openapi_signature(spec: dict) -> dict:
    signature: dict[str, object] = {
        "title": spec.get("info", {}).get("title"),
        "version": spec.get("info", {}).get("version"),
        "paths": {},
    }

    paths: dict = spec.get("paths", {})
    normalized_paths: dict[str, object] = {}

    for path in sorted(paths.keys()):
        methods = paths[path]
        normalized_methods: dict[str, object] = {}
        for method in sorted(methods.keys()):
            operation = methods[method]
            parameters = operation.get("parameters", [])
            normalized_methods[method] = {
                "parameters": [
                    {
                        "name": param.get("name"),
                        "in": param.get("in"),
                        "required": param.get("required", False),
                        "type": _param_type(param),
                    }
                    for param in parameters
                ],
                "responses": sorted(operation.get("responses", {}).keys()),
            }
        normalized_paths[path] = normalized_methods

    signature["paths"] = normalized_paths
    return signature


def test_openapi_signature_snapshot() -> None:
    signature = _build_openapi_signature(app.openapi())
    if os.getenv("UPDATE_OPENAPI_SNAPSHOT") == "1":
        SNAPSHOT_PATH.write_text(json.dumps(signature, ensure_ascii=False, indent=2), encoding="utf-8")
    expected = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    assert signature == expected
