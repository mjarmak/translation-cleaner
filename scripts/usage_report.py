import json
import csv
import argparse
import time
from pathlib import Path
from collections import Counter

VALID_SUFFIXES = {".ts", ".html", ".js", ".jsx", ".tsx"}


def log(msg: str):
    print(f"[i18n-usage] {msg}")


def load_flat_keys(flat_path: Path) -> list[str]:
    log(f"Loading flattened keys from: {flat_path}")
    start = time.time()

    with open(flat_path, encoding="utf-8") as f:
        data = json.load(f)

    keys = list(data.keys())

    log(f"Loaded {len(keys)} keys in {time.time() - start:.2f}s")
    return keys


def scan_project(src_path: Path, keys: list[str], ignore_case: bool, verbose: bool) -> Counter:
    log(f"Scanning project folder: {src_path}")
    log(f"Case insensitive mode: {'ON' if ignore_case else 'OFF'}")

    start = time.time()

    counter = Counter()
    files_scanned = 0
    total_matches = 0

    # Prepare keys
    if ignore_case:
        key_lookup = {k.lower(): k for k in keys}
        search_keys = list(key_lookup.keys())
    else:
        key_lookup = {k: k for k in keys}
        search_keys = keys

    all_files = list(src_path.rglob("*"))
    log(f"Discovered {len(all_files)} total files")

    for file in all_files:
        if file.suffix.lower() not in VALID_SUFFIXES:
            continue

        files_scanned += 1

        if verbose and files_scanned % 50 == 0:
            log(f"Processed {files_scanned} source files...")

        try:
            text = file.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            log(f"⚠️ Skipped unreadable file: {file} ({e})")
            continue

        if ignore_case:
            text_to_search = text.lower()
        else:
            text_to_search = text

        file_matches = 0

        for skey in search_keys:
            occurrences = text_to_search.count(skey)
            if occurrences:
                original_key = key_lookup[skey]
                counter[original_key] += occurrences
                file_matches += occurrences

        total_matches += file_matches

        if verbose and file_matches:
            log(f"Match in {file}: {file_matches}")

    duration = time.time() - start
    log(f"Scan complete in {duration:.2f}s")
    log(f"Source files scanned: {files_scanned}")
    log(f"Total key matches found: {total_matches}")

    return counter


def write_csv(output_path: Path, all_keys: list[str], counter: Counter):
    log(f"Writing CSV report to: {output_path}")
    start = time.time()

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["key", "usage_count"])

        for key in sorted(all_keys):
            writer.writerow([key, counter.get(key, 0)])

    log(f"CSV written in {time.time() - start:.2f}s")


def print_summary(keys: list[str], counter: Counter):
    used = sum(1 for k in keys if counter.get(k, 0) > 0)
    unused = len(keys) - used

    log("📊 Summary")
    log(f"Used keys:   {used}")
    log(f"Unused keys: {unused}")

    top_used = counter.most_common(10)
    if top_used:
        log("🔥 Top used keys:")
        for key, count in top_used:
            log(f"   {key}: {count}")

    unused_keys = [k for k in keys if counter.get(k, 0) == 0][:10]
    if unused_keys:
        log("🧹 Sample unused keys:")
        for k in unused_keys:
            log(f"   {k}")


def main():
    parser = argparse.ArgumentParser(
        description="Count translation key usage in Angular project"
    )
    parser.add_argument("flat_json", help="Flattened i18n JSON file")
    parser.add_argument("--src", default="src", help="Source directory")
    parser.add_argument("--out", default="usage_report.csv", help="Output CSV")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument(
        "--ignore-case",
        action="store_true",
        help="Case-insensitive key matching",
    )

    args = parser.parse_args()

    overall_start = time.time()
    log("🚀 Starting i18n usage analysis")

    flat_path = Path(args.flat_json)
    src_path = Path(args.src)
    out_path = Path(args.out)

    if not flat_path.exists():
        raise FileNotFoundError(f"Flatten file not found: {flat_path}")

    if not src_path.exists():
        raise FileNotFoundError(f"Source folder not found: {src_path}")

    # Load keys
    keys = load_flat_keys(flat_path)

    # Scan project
    counter = scan_project(
        src_path,
        keys,
        ignore_case=args.ignore_case,
        verbose=args.verbose,
    )

    # Write CSV
    write_csv(out_path, keys, counter)

    # Summary
    print_summary(keys, counter)

    log(f"✅ Done in {time.time() - overall_start:.2f}s")


if __name__ == "__main__":
    main()