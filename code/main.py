"""CLI entry point for the architecture metrics and comparator tool.

Usage
-----
    python main.py metrics <diagram.mmd>
    python main.py compare <base.mmd> <generated.mmd>

Both modes print results as formatted JSON to stdout.
"""

from __future__ import annotations

import json
import sys


def cmd_metrics(args: list[str]) -> None:
    if len(args) != 1:
        print("Usage: python main.py metrics <diagram.mmd>", file=sys.stderr)
        sys.exit(1)

    from mermaid_utils import parse_mermaid_file
    from metrics import calculate_all_metrics

    path = args[0]
    graph = parse_mermaid_file(path)
    result = calculate_all_metrics(graph)
    print(json.dumps(result, indent=2))


def cmd_compare(args: list[str]) -> None:
    if len(args) != 2:
        print(
            "Usage: python main.py compare <base.mmd> <generated.mmd>",
            file=sys.stderr,
        )
        sys.exit(1)

    from mermaid_utils import parse_mermaid_file
    from comparator import compare_architectures

    base_path, generated_path = args
    base = parse_mermaid_file(base_path)
    generated = parse_mermaid_file(generated_path)
    result = compare_architectures(base, generated)
    print(json.dumps(result, indent=2))


COMMANDS: dict[str, callable] = {
    "metrics": cmd_metrics,
    "compare": cmd_compare,
}


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        modes = ", ".join(COMMANDS)
        print(f"Usage: python main.py <mode> <args>", file=sys.stderr)
        print(f"Available modes: {modes}", file=sys.stderr)
        sys.exit(1)

    mode = sys.argv[1]
    COMMANDS[mode](sys.argv[2:])


if __name__ == "__main__":
    main()
