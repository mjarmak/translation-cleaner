import json
import re
import argparse
from pathlib import Path
from collections import Counter


TRANSLATE_PATTERNS = [
    re.compile(r"""['"]([\w.-]+)['"]\s*\|\s*translate"""),  # {{ 'key' | translate }}
    re.compile(r"""translate\.instant\(['"]([\w.-]+)['"]\)"""),
    re.compile(r"""translate\.get\(['"]([\w.-]+)['"]\)"""),
]


def extract_keys_from_file(path: Path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    found = []

    for pattern in TRANSLATE_PATTERNS:
        found.extend(pattern.findall(text))

    return found


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("flat_json")
    parser.add_argument("--src", default="src")
    parser.add_argument("--out", default="usage_report.json")
    args = parser.parse_args()

    with open(args.flat_json, encoding="utf-8") as f:
        keys = set(json.load(f).keys())

    counter = Counter()

    for file in Path(args.src).rglob("*"):
        if file.suffix in {".ts", ".html"}:
            for key in extract_keys_from_file(file):
                if key in keys:
                    counter[key] += 1

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(counter.most_common(), f, indent=2)

    print(f"✅ Report generated: {args.out}")


if __name__ == "__main__":
    main()