"""CLI entry point: python -m app.evaluation --input ... --settings ..."""

from __future__ import annotations

import argparse
import json
import sys

from app.evaluation.pipeline import EvaluationInputError, run_evaluation


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate authorized observed FCFS and slot-policy records.")
    parser.add_argument("--input", required=True, help="Authorized event-level CSV; not a synthetic fixture.")
    parser.add_argument("--settings", required=True, help="Protocol and provenance JSON settings.")
    parser.add_argument("--output", help="Optional JSON output path; default writes to stdout.")
    args = parser.parse_args()
    try:
        result = run_evaluation(args.input, args.settings)
    except EvaluationInputError as exc:
        print(json.dumps({"result_status": "invalid_input", "error": str(exc)}, indent=2), file=sys.stdout)
        return 2
    serialized = json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(serialized + "\n")
    else:
        print(serialized)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
