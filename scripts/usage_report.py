import json
import csv
import argparse
from pathlib import Path
from collections import Counter

VALID_SUFFIXES = {".ts", ".html"}


def load_flat_keys(flat_path: Path) -> set[str]:
    with open(flat_path, encoding="utf-8") as f:
        data = json.load(f)
    return set(data.keys())


def scan_project(src_path: Path, keys: set[str]) -> Counter:
    """
    Count raw string occurrences of each key in the project.
    """
    counter = Counter()
    files_scanned = 0

    # Pre-build lookup for speed
    keys_list = sorted(keys)

    for file in src_path.rglob("*"):
        if file.suffix.lower() not in VALID_SUFFIXES:
            continue

        files_scanned += 1

        try:
            text = file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        for key in keys_list:
            occurrences = text.count(key)
            if occurrences:
                counter[key] += occurrences

    print(f"🔍 Scanned {files_scanned} files")
    return counter


def write_csv(output_path: Path, all_keys: set[str], counter: Counter):
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["key", "usage_count"])

        for key in sorted(all_keys):
            writer.writerow([key, counter.get(key, 0)])

    print(f"✅ CSV written: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Count translation key usage in Angular project"
    )
    parser.add_argument("flat_json", help="Flattened i18n JSON file")
    parser.add_argument("--src", default="src", help="Source directory")
    parser.add_argument("--out", default="usage_report.csv", help="Output CSV")

    args = parser.parse_args()

    flat_path = Path(args.flat_json)
    src_path = Path(args.src)
    out_path = Path(args.out)

    if not flat_path.exists():
        raise FileNotFoundError(f"Flatten file not found: {flat_path}")

    if not src_path.exists():
        raise FileNotFoundError(f"Source folder not found: {src_path}")

    # Load keys
    keys = load_flat_keys(flat_path)
    print(f"📦 Loaded {len(keys)} translation keys")

    # Scan
    counter = scan_project(src_path, keys)

    # Write CSV
    write_csv(out_path, keys, counter)

    # Summary
    used = sum(1 for k in keys if counter.get(k, 0) > 0)
    unused = len(keys) - used

    print("\n📊 Summary")
    print(f"   Used keys:   {used}")
    print(f"   Unused keys: {unused}")


if __name__ == "__main__":
    main()