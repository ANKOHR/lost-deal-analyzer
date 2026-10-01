"""Local-only CLI. Example: lda fixtures --out demo; lda run --input demo."""
import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
from .core import InputError, analyze, REASONS
from .report import render


def atomic_write(path, text):
    path = Path(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=path.parent, delete=False) as stream:
            temporary = stream.name
            stream.write(text)
        os.replace(temporary, path)
    except OSError as exc:
        raise InputError(f"WriteError: {path}: {exc.strerror}") from exc
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)


def load_inputs(directory):
    directory = Path(directory)
    if not directory.is_dir():
        raise InputError(f"MissingInput: {directory}: use lda fixtures --out <dir> or provide an existing input directory")
    documents = []
    for path in sorted(directory.iterdir()):
        if path.name in ("expectations.json", "SYNTHETIC.md") or path.is_dir():
            continue
        if path.suffix.lower() != ".json":
            raise InputError(f"SchemaError: {path.name}: line 1: field format: only JSON input documents supported")
        try:
            doc = json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=unique_keys)
        except json.JSONDecodeError as exc:
            raise InputError(f"ParseError: {path.name}: line {exc.lineno}: {exc.msg}") from exc
        except (UnicodeError, ValueError) as exc:
            raise InputError(f"ParseError: {path.name}: line 1: {exc}") from exc
        documents.append((path.name, doc))
    return documents


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON field {key}")
        result[key] = value
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description="Analyze explicitly recorded loss reasons. Local files only.")
    sub = parser.add_subparsers(dest="command", required=True)
    fixtures = sub.add_parser("fixtures", help="Generate 200 labelled synthetic records", epilog="Example: lda fixtures --out demo")
    fixtures.add_argument("--out", required=True)
    run = sub.add_parser("run", help="Validate and aggregate JSON inputs", epilog="Example: lda run --input demo")
    run.add_argument("--input", required=True)
    run.add_argument("--state", default=".lda/result.json")
    report = sub.add_parser("report", help="Render computed report with provenance", epilog="Example: lda report --format md")
    report.add_argument("--format", choices=("md", "json"), default="md")
    report.add_argument("--state", default=".lda/result.json")
    report.add_argument("--out")
    for name, help_text in (("reasons", "Show recorded loss reasons and supporting IDs"), ("audit", "Validate schema, duplicates, dates and reconciliation")):
        command = sub.add_parser(name, help=help_text, epilog=f"Example: lda {name} --input demo")
        command.add_argument("--input", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "fixtures":
            from .fixtures import generate
            generate(args.out)
            print("Generated 200 synthetic records with labelled hand-computed expectations.")
        elif args.command == "report":
            path = Path(args.state)
            if not path.is_file():
                raise InputError(f"MissingInput: {path}: run lda run --input <dir> first")
            try:
                result = json.loads(path.read_text(encoding="utf-8"))
                output = render(result, args.format)
            except (ValueError, KeyError, TypeError) as exc:
                raise InputError(f"StateError: {path}: invalid result; rerun lda run --input <dir>") from exc
            if args.out:
                atomic_write(args.out, output)
            else:
                print(output, end="")
        else:
            result = analyze(load_inputs(args.input))
            if args.command == "run":
                path = Path(args.state)
                path.parent.mkdir(parents=True, exist_ok=True)
                atomic_write(path, render(result, "json"))
            print(render(result, "json"), end="")
        return 0
    except (InputError, OSError) as exc:
        print(str(exc) if isinstance(exc, InputError) else f"FileError: {exc.filename}: {exc.strerror}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
