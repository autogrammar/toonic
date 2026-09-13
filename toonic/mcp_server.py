"""Toonic MCP server — dependency-free stdio JSON-RPC.

Adopts wellmanifest/poa (typed tools, closed inputSchema, fail-closed
dispatch) and wellmanifest/logs (append-only hash-chained JSONL event
stream under $XDG_STATE_HOME/toonic/mcp-events.jsonl, overridable with
TOONIC_MCP_EVENT_LOG).
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Callable

_PROTOCOL_VERSION = "2024-11-05"
_NOTIFICATIONS = frozenset({"notifications/initialized", "notifications/cancelled"})

SERVER_NAME = "toonic"
try:
    from importlib.metadata import version as _pkg_version

    SERVER_VERSION = _pkg_version("toonic")
except Exception:
    SERVER_VERSION = "0.0.0"

_ZERO_HASH = "0" * 64


def _event_log_path() -> Path:
    override = os.environ.get("TOONIC_MCP_EVENT_LOG")
    if override:
        return Path(override)
    state_home = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state"))
    return state_home / "toonic" / "mcp-events.jsonl"


def _emit_event(tool: str, status: str, duration_ms: int, detail: str = "") -> None:
    """Append one hash-chained event; logging failure never breaks a tool call."""
    try:
        path = _event_log_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        prev = _ZERO_HASH
        if path.exists() and path.stat().st_size:
            with path.open("rb") as fh:
                fh.seek(0, os.SEEK_END)
                tail = fh.read(65536).decode("utf-8", errors="replace")
            last = tail.rstrip().rsplit("\n", 1)[-1]
            prev = json.loads(last).get("event_hash", _ZERO_HASH)
        event = {
            "schema": "toonic.mcp/event/v1",
            "event_id": f"event:{uuid.uuid4().hex[:24]}",
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "actor": "agent:mcp",
            "tool": tool,
            "status": status,
            "duration_ms": duration_ms,
            "detail": detail[:200],
            "prev_hash": prev,
        }
        body = json.dumps(event, sort_keys=True)
        event["event_hash"] = hashlib.sha256(body.encode()).hexdigest()
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event) + "\n")
    except Exception:
        pass


def _tool_to_spec(args: dict[str, Any]) -> str:
    from toonic.pipeline import Pipeline

    spec = Pipeline.to_spec(
        args["source"], fmt=args.get("fmt", "toon"), output=args.get("output")
    )
    return spec


def _tool_reproduce(args: dict[str, Any]) -> str:
    from toonic.pipeline import Pipeline

    result = Pipeline.reproduce(
        args["spec"], output=args.get("output"), target_fmt=args.get("target_fmt")
    )
    return json.dumps(
        {
            "success": result.success,
            "output_file": result.output_file,
            "spec_format": result.spec_format,
            "error": result.error,
            "duration_seconds": result.duration_seconds,
        },
        indent=2,
    )


def _tool_roundtrip(args: dict[str, Any]) -> str:
    from toonic.pipeline import Pipeline

    result = Pipeline.roundtrip(
        args["source"], fmt=args.get("fmt", "toon"), output=args.get("output")
    )
    return json.dumps(
        {
            "success": result.success,
            "output_file": result.output_file,
            "spec_tokens": result.spec_tokens,
            "error": result.error,
            "duration_seconds": result.duration_seconds,
        },
        indent=2,
    )


def _tool_batch(args: dict[str, Any]) -> str:
    from toonic.pipeline import Pipeline

    results = Pipeline.batch(
        args["source_dir"],
        fmt=args.get("fmt", "toon"),
        output_dir=args.get("output_dir"),
        extensions=args.get("extensions"),
    )
    return json.dumps({"count": len(results), "results": results}, indent=2)


def _tool_formats(_args: dict[str, Any]) -> str:
    from toonic.pipeline import Pipeline

    return json.dumps(Pipeline.formats(), indent=2)


_SOURCE_PROPERTY = {
    "source": {"type": "string", "description": "Path to the source file"},
}
_FMT_PROPERTY = {
    "fmt": {
        "type": "string",
        "enum": ["toon", "yaml", "json"],
        "default": "toon",
        "description": "Spec output format",
    }
}

TOOL_SCHEMAS: dict[str, dict[str, Any]] = {
    "toonic_to_spec": {
        "name": "toonic_to_spec",
        "description": "Convert any source file to a TOON/YAML/JSON spec (toonic Pipeline).",
        "inputSchema": {
            "type": "object",
            "properties": {
                **_SOURCE_PROPERTY,
                **_FMT_PROPERTY,
                "output": {
                    "type": "string",
                    "description": "Optional output file path for the spec",
                },
            },
            "required": ["source"],
        },
    },
    "toonic_reproduce": {
        "name": "toonic_reproduce",
        "description": "Reproduce a file from a toon/yaml/json spec.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "spec": {"type": "string", "description": "Path to the spec file"},
                "output": {"type": "string", "description": "Output file path"},
                "target_fmt": {
                    "type": "string",
                    "description": "Optional target format override",
                },
            },
            "required": ["spec"],
        },
    },
    "toonic_roundtrip": {
        "name": "toonic_roundtrip",
        "description": "source → spec → reproduced file in one pass; reports success and token estimate.",
        "inputSchema": {
            "type": "object",
            "properties": {
                **_SOURCE_PROPERTY,
                **_FMT_PROPERTY,
                "output": {"type": "string", "description": "Output file path"},
            },
            "required": ["source"],
        },
    },
    "toonic_batch": {
        "name": "toonic_batch",
        "description": "Convert every handled file in a directory to specs.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "source_dir": {
                    "type": "string",
                    "description": "Directory to scan",
                },
                **_FMT_PROPERTY,
                "output_dir": {
                    "type": "string",
                    "description": "Directory for generated specs",
                },
                "extensions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional extension whitelist, e.g. ['.py', '.md']",
                },
            },
            "required": ["source_dir"],
        },
    },
    "toonic_formats": {
        "name": "toonic_formats",
        "description": "List registered format handlers, categories and dependency availability.",
        "inputSchema": {"type": "object", "properties": {}},
    },
}

TOOL_HANDLERS: dict[str, Callable[[dict[str, Any]], str]] = {
    "toonic_to_spec": _tool_to_spec,
    "toonic_reproduce": _tool_reproduce,
    "toonic_roundtrip": _tool_roundtrip,
    "toonic_batch": _tool_batch,
    "toonic_formats": _tool_formats,
}


def _handle_initialize(request_id: Any, params: dict[str, Any] | None) -> dict[str, Any]:
    client_version = (params or {}).get("protocolVersion", _PROTOCOL_VERSION)
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "protocolVersion": client_version,
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            "capabilities": {"tools": {}},
        },
    }


def _handle_tools_list(request_id: Any) -> dict[str, Any]:
    tools = [
        {
            "name": schema["name"],
            "description": schema["description"],
            "inputSchema": schema["inputSchema"],
        }
        for schema in TOOL_SCHEMAS.values()
    ]
    return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": tools}}


def _handle_tools_call(request_id: Any, params: dict[str, Any]) -> dict[str, Any]:
    tool_name = params.get("name")
    arguments = params.get("arguments", {}) or {}

    if tool_name not in TOOL_HANDLERS:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"},
        }

    start = time.monotonic()
    try:
        result = TOOL_HANDLERS[tool_name](arguments)
        _emit_event(tool_name, "ok", int((time.monotonic() - start) * 1000))
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"content": [{"type": "text", "text": result}]},
        }
    except Exception as exc:
        _emit_event(
            tool_name, "error", int((time.monotonic() - start) * 1000), str(exc)
        )
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32603, "message": f"Tool execution failed: {exc}"},
        }


def handle_request(request: dict[str, Any]) -> dict[str, Any]:
    method = request.get("method", "")
    params = request.get("params", {}) or {}
    request_id = request.get("id")

    if method in _NOTIFICATIONS:
        return {}
    if method == "initialize":
        return _handle_initialize(request_id, params)
    if method == "tools/list":
        return _handle_tools_list(request_id)
    if method == "tools/call":
        return _handle_tools_call(request_id, params)

    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": -32601, "message": f"Method '{method}' not found"},
    }


def run_server() -> None:
    print("Toonic MCP Server started", file=sys.stderr)
    print(f"Available tools: {', '.join(sorted(TOOL_SCHEMAS))}", file=sys.stderr)

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            response = handle_request(request)
            if response:
                print(json.dumps(response), flush=True)
        except json.JSONDecodeError as exc:
            print(
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "error": {"code": -32700, "message": f"Parse error: {exc}"},
                    }
                ),
                flush=True,
            )
        except Exception as exc:
            print(
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "error": {"code": -32603, "message": f"Internal error: {exc}"},
                    }
                ),
                flush=True,
            )


def main() -> None:
    run_server()


if __name__ == "__main__":
    main()
