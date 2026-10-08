"""
Toonic CLI — command-line interface
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Optional, Callable, Dict, Any

from toonic.pipeline import Pipeline


# ══════════════════════════════════════════════════════════════
# CLI Command Handlers
# ══════════════════════════════════════════════════════════════


def _cmd_spec(parsed: Any) -> None:
    """Handle 'spec' command - convert source to spec."""
    source = Path(parsed.source)
    if source.is_dir():
        results = Pipeline.batch(str(source), fmt=parsed.fmt, output_dir=parsed.output)
        print(f"Przetworzono {len(results)} plików")
    else:
        spec = Pipeline.to_spec(str(source), fmt=parsed.fmt, output=parsed.output)
        if not parsed.output:
            print(spec)


def _cmd_reproduce(parsed: Any) -> None:
    """Handle 'reproduce' command - spec to file."""
    result = Pipeline.reproduce(
        parsed.spec, output=parsed.output, target_fmt=parsed.target_fmt
    )
    if result.success:
        print(
            f"OK Reprodukcja: {result.output_file or 'stdout'} ({result.duration_seconds:.2f}s)"
        )
    else:
        print(f"ERROR: {result.error}", file=sys.stderr)


def _cmd_formats(parsed: Any) -> None:
    """Handle 'formats' command - list supported formats."""
    info = Pipeline.formats()
    print(f"Toonic — {info['total_handlers']} handlerów\n")
    for cat, exts in info["categories"].items():
        print(f"  {cat}: {', '.join(exts)}")
    if parsed.check:
        print("\nDostępność zależności:")
        for key, ok in info["available"].items():
            status = "OK" if ok else "MISSING"
            print(f"  [{status}] {key}")


def _cmd_init(parsed: Any) -> None:
    """Handle 'init' command - scaffold new project."""
    from toonic.autopilot.scaffold import ProjectScaffold

    spec, files = ProjectScaffold.init(
        description=parsed.description,
        name=parsed.name,
        language=parsed.lang,
        output_dir=parsed.output,
    )
    print(f"\n  Project '{spec.name}' created!")
    print("  ─────────────────────────────────")
    print(f"  Type:     {spec.project_type}")
    print(f"  Language: {spec.language}")
    print(f"  Files:    {len(files)}")
    print(f"  Dir:      {parsed.output or './' + spec.name}/")
    print("\n  Next steps:")
    print(f"    cd {spec.name}")
    print("    toonic autopilot . --goal 'build MVP'")
    print()


def _cmd_examples_list() -> None:
    """List all examples."""
    from examples.run_all import list_examples

    list_examples()


def _cmd_examples_verify() -> int:
    """Verify all examples. Returns exit code."""
    from examples.run_all import verify_all

    ok = verify_all()
    return 0 if ok else 1


def _cmd_examples_show(name: str) -> None:
    """Show example details."""
    from examples.run_all import show_example

    show_example(name)


def _cmd_examples_preset(name: str, sources: List[str]) -> int:
    """Build config from preset (dry run). Returns exit code."""
    from toonic.server.quick import PRESETS

    if name not in PRESETS:
        print(f"Unknown preset: {name}")
        print(f"Available: {', '.join(PRESETS.keys())}")
        return 1

    sources = sources or ["./examples/code-analysis/sample-project/"]
    builder = PRESETS[name]["fn"](*sources)
    cfg = builder.build_config()
    print(f"  Preset:  {name}")
    print(f"  Goal:    {cfg.goal}")
    print(f"  Sources: {len(cfg.sources)}")
    for s in cfg.sources:
        print(f"    [{s.category}] {s.path_or_url}")
    print(f"\n  To run: from toonic.server.quick import {name.replace('-', '_')}")
    print(f"  {name.replace('-', '_')}({', '.join(repr(s) for s in sources)}).run()")
    return 0


def _cmd_examples_run_demo(script_name: str) -> int:
    """Run a demo script. Returns exit code."""
    import subprocess
    from pathlib import Path as P

    script = P("examples/programmatic-api") / script_name
    if not script.exists():
        script = P("examples/programmatic-api") / f"demo_{script_name}.py"

    if script.exists():
        subprocess.run([sys.executable, str(script)])
        return 0
    else:
        print(f"Script not found: {script_name}")
        return 1


def _cmd_examples(parsed: Any) -> int:
    """Handle 'examples' command. Returns exit code."""
    if parsed.list:
        _cmd_examples_list()
    elif parsed.verify:
        return _cmd_examples_verify()
    elif parsed.show:
        _cmd_examples_show(parsed.show)
    elif parsed.preset:
        return _cmd_examples_preset(parsed.preset, parsed.sources)
    elif parsed.run_demo:
        return _cmd_examples_run_demo(parsed.run_demo)
    else:
        _cmd_examples_list()
    return 0


def _event_printer(event_type: str, data: Dict[str, Any]) -> None:
    """Print autopilot events to console."""
    if event_type == "iteration_start":
        print(f"\n── Iteration {data['iteration']} ──")
    elif event_type == "llm_response":
        print(f"  LLM: {data.get('description', '')[:80]}")
        print(f"  Files: {data.get('files_count', 0)}")
    elif event_type == "iteration_done":
        written = data.get("files_written", [])
        if written:
            for f in written:
                print(f"  ✓ {f}")
        if data.get("error"):
            print(f"  ✗ {data['error'][:100]}")
    elif event_type == "complete":
        print(f"\n  ✓ ROADMAP complete in {data['iterations']} iterations!")
    elif event_type == "error":
        print(f"  ERROR: {data.get('error', data.get('message', ''))}")


def _cmd_autopilot(parsed: Any) -> None:
    """Handle 'autopilot' command - autonomous development loop."""
    import asyncio
    from toonic.autopilot.loop import AutopilotLoop, AutopilotConfig

    config = AutopilotConfig(
        project_dir=parsed.project_dir,
        goal=parsed.goal,
        max_iterations=parsed.max_iter,
        interval_s=parsed.interval,
        model=parsed.model,
        dry_run=parsed.dry_run,
        auto_test=not parsed.no_test,
    )
    loop = AutopilotLoop(config)

    try:
        results = asyncio.run(loop.run(on_event=_event_printer))
        print(f"\nAutopilot finished: {len(results)} actions")
    except KeyboardInterrupt:
        print("\nAutopilot stopped.")


# ══════════════════════════════════════════════════════════════
# CLI Router
# ══════════════════════════════════════════════════════════════

CommandHandler = Callable[[Any], Optional[int]]


def _get_command_handler(cmd: str) -> Optional[CommandHandler]:
    """Get handler for a command. Returns None for unknown commands."""
    handlers: Dict[str, CommandHandler] = {
        "spec": _cmd_spec,
        "reproduce": _cmd_reproduce,
        "formats": _cmd_formats,
        "init": _cmd_init,
        "examples": _cmd_examples,
        "autopilot": _cmd_autopilot,
    }
    return handlers.get(cmd)


def _build_argument_parser() -> Any:
    """Build and return the argument parser."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="toonic",
        description="Toonic — Universal TOON Format Platform",
    )
    subparsers = parser.add_subparsers(dest="command", help="Komenda")

    # --- spec ---
    spec_parser = subparsers.add_parser("spec", help="Plik źródłowy → spec")
    spec_parser.add_argument("source", help="Plik lub katalog źródłowy")
    spec_parser.add_argument(
        "--fmt",
        default="toon",
        choices=["toon", "yaml", "json"],
        help="Format spec (domyślnie: toon)",
    )
    spec_parser.add_argument("-o", "--output", help="Plik wyjściowy")

    # --- reproduce ---
    repro_parser = subparsers.add_parser("reproduce", help="Spec → odtworzony plik")
    repro_parser.add_argument("spec", help="Plik spec (.toon, .yaml, .json)")
    repro_parser.add_argument("-o", "--output", help="Plik wyjściowy")
    repro_parser.add_argument(
        "--as", dest="target_fmt", help="Format docelowy (transpilacja)"
    )

    # --- formats ---
    fmt_parser = subparsers.add_parser("formats", help="Lista obsługiwanych formatów")
    fmt_parser.add_argument("--check", action="store_true", help="Sprawdź zależności")

    # --- init ---
    init_parser = subparsers.add_parser(
        "init", help="Scaffold new project from description"
    )
    init_parser.add_argument(
        "description", help="Project description (natural language)"
    )
    init_parser.add_argument("--name", default="", help="Project name")
    init_parser.add_argument("--lang", default="", help="Language (python, javascript)")
    init_parser.add_argument("-o", "--output", default="", help="Output directory")

    # --- examples ---
    ex_parser = subparsers.add_parser(
        "examples", help="List, verify, run examples & presets"
    )
    ex_parser.add_argument(
        "--list", "-l", action="store_true", help="List examples & presets"
    )
    ex_parser.add_argument("--verify", action="store_true", help="Verify all examples")
    ex_parser.add_argument("--show", type=str, help="Show example details")
    ex_parser.add_argument(
        "--preset", "-p", type=str, help="Build config from preset (dry)"
    )
    ex_parser.add_argument("--run-demo", type=str, help="Run a demo script")
    ex_parser.add_argument("sources", nargs="*", help="Sources for preset")

    # --- autopilot ---
    auto_parser = subparsers.add_parser("autopilot", help="Autonomous development loop")
    auto_parser.add_argument(
        "project_dir", nargs="?", default=".", help="Project directory"
    )
    auto_parser.add_argument(
        "--goal", "-g", default="build MVP", help="Development goal"
    )
    auto_parser.add_argument("--max-iter", type=int, default=20, help="Max iterations")
    auto_parser.add_argument(
        "--interval", type=float, default=10.0, help="Seconds between iterations"
    )
    auto_parser.add_argument("--model", "-m", default="", help="LLM model override")
    auto_parser.add_argument(
        "--dry-run", action="store_true", help="Show changes without writing"
    )
    auto_parser.add_argument("--no-test", action="store_true", help="Skip auto-testing")

    return parser


def cli_main(args: List[str] | None = None) -> None:
    try:
        from .autoupdate import check_for_updates
        check_for_updates("toonic")
    except Exception:
        pass
    """Uproszczony CLI — dwa główne polecenia.

    toonic spec <source> [--fmt toon] [-o output]
    toonic reproduce <spec> [-o output] [--as target-format]
    toonic formats [--check]
    toonic init "description" [--name NAME] [--lang python]
    toonic autopilot [DIR] [--goal GOAL] [--max-iter N]
    toonic examples [--list] [--verify] [--preset NAME] [SOURCES...]
    """
    parser = _build_argument_parser()
    parsed = parser.parse_args(args)

    if not parsed.command:
        parser.print_help()
        return

    handler = _get_command_handler(parsed.command)
    if handler is None:
        parser.print_help()
        return

    exit_code = handler(parsed)
    if exit_code:
        sys.exit(exit_code)


if __name__ == "__main__":
    cli_main()
