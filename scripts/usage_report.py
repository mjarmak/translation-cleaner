import json
import csv
import argparse
import time
from pathlib import Path
from collections import Counter

VALID_SUFFIXES = {".ts", ".html", ".js", ".jsx", ".tsx"}


def log(msg: str):
    print(f"[i18n-usage] {msg}")


def load_flat_keys(flat_path: Path) -> tuple[list[str], dict]:
    log(f"Loading flattened keys from: {flat_path}")
    start = time.time()

    with open(flat_path, encoding="utf-8") as f:
        data = json.load(f)

    keys = list(data.keys())

    log(f"Loaded {len(keys)} keys in {time.time() - start:.2f}s")
    return keys, data


def load_language_file(flat_path: Path) -> dict:
    """Load a language file and return key-value mapping."""
    if not flat_path.exists():
        return {}

    try:
        with open(flat_path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log(f"⚠️ Could not load language file {flat_path}: {e}")
        return {}


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


def write_csv(output_path: Path, all_keys: list[str], counter: Counter, en_data: dict, language_data: dict, ignore_case: bool = False):
    log(f"Writing CSV report to: {output_path}")
    start = time.time()

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Build header
        header = ["key", "en_value", "usage_count"]
        # Add language-specific columns if we have data
        language_codes = sorted(language_data.keys()) if language_data else []
        for lang_code in language_codes:
            header.append(f"{lang_code}_value")

        writer.writerow(header)

        for key in sorted(all_keys):
            row = [
                key,
            ]

            # Add English value(s)
            if ignore_case:
                # For case-insensitive mode, collect all matching English values
                key_lower = key.lower()
                matching_en_values = []
                for k, v in en_data.items():
                    if k.lower() == key_lower and v:  # Only add non-empty values
                        matching_en_values.append(v)
                # Join all unique values with |
                en_value = "|".join(dict.fromkeys(matching_en_values)) if matching_en_values else ""
                row.append(en_value)
            else:
                row.append(en_data.get(key, ""))

            row.append(counter.get(key, 0))

            # Add language values if available
            for lang_code in language_codes:
                lang_dict = language_data.get(lang_code, {})
                if ignore_case:
                    # For case-insensitive mode, collect all matching values
                    key_lower = key.lower()
                    matching_values = []
                    for k, v in lang_dict.items():
                        if k.lower() == key_lower and v:  # Only add non-empty values
                            matching_values.append(v)
                    # Join all unique values with |
                    value = "|".join(dict.fromkeys(matching_values)) if matching_values else ""
                    row.append(value)
                else:
                    row.append(lang_dict.get(key, ""))

            writer.writerow(row)

    log(f"CSV written in {time.time() - start:.2f}s")


def print_summary(keys: list[str], counter: Counter):
    used = sum(1 for k in keys if counter.get(k, 0) > 0)
    unused = len(keys) - used

    log("Summary")
    log(f"Used keys:   {used}")
    log(f"Unused keys: {unused}")

    top_used = counter.most_common(10)
    if top_used:
        log("Top used keys:")
        for key, count in top_used:
            log(f"   {key}: {count}")

    unused_keys = [k for k in keys if counter.get(k, 0) == 0][:10]
    if unused_keys:
        log("Sample unused keys:")
        for k in unused_keys:
            log(f"   {k}")


def main():
    parser = argparse.ArgumentParser(
        description="Count translation key usage in Angular project"
    )
    parser.add_argument("flat_json", help="Flattened i18n JSON file (English)")
    parser.add_argument("--src", default="src", help="Source directory")
    parser.add_argument("--out", default="usage_report.csv", help="Output CSV")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument(
        "--ignore-case",
        action="store_true",
        help="Case-insensitive key matching",
    )
    parser.add_argument(
        "--languages",
        default="",
        help="Comma-separated list of language file paths (e.g., './output/fr.flat.json,./output/nl.flat.json')",
    )

    args = parser.parse_args()

    overall_start = time.time()
    log("Starting i18n usage analysis")

    flat_path = Path(args.flat_json)
    src_path = Path(args.src)
    out_path = Path(args.out)

    if not flat_path.exists():
        parser.error(f"Flatten file not found: {flat_path}")

    if not src_path.exists():
        parser.error(f"Source folder not found: {src_path}")

    # Load English keys and values
    keys, en_data = load_flat_keys(flat_path)

    # Load other language files if provided
    language_data = {}
    if args.languages:
        lang_files = [p.strip() for p in args.languages.split(",")]
        for lang_file in lang_files:
            lang_path = Path(lang_file)
            if not lang_path.exists():
                parser.error(f"Language file not found: {lang_path}")
            # Extract language code from filename (e.g., 'fr.flat.json' -> 'fr')
            lang_code = lang_path.stem.split(".")[0]
            log(f"Loading language file: {lang_path} (code: {lang_code})")
            language_data[lang_code] = load_language_file(lang_path)

    # Scan project
    counter = scan_project(
        src_path,
        keys,
        ignore_case=args.ignore_case,
        verbose=args.verbose,
    )

    # Write CSV
    write_csv(out_path, keys, counter, en_data, language_data)
    write_csv(out_path, keys, counter, en_data, language_data, ignore_case=args.ignore_case)

    # Summary
    print_summary(keys, counter)

    log(f"Done in {time.time() - overall_start:.2f}s")


if __name__ == "__main__":
    main()