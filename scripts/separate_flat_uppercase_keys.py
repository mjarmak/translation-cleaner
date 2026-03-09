import json
import argparse
from pathlib import Path


def log(msg: str):
    print(f"[i18n-separate] {msg}")


def is_all_uppercase(value: str) -> bool:
    """Check if value contains only uppercase letters (and non-letter characters)."""
    letters_only = ''.join(c for c in value if c.isalpha())
    if not letters_only:  # No letters at all
        return False
    return letters_only == letters_only.upper()


def separate_file(data, underscore_keys, uppercase_keys):
    """Separate a JSON file based on underscore and uppercase key sets."""
    underscore_data = {}
    uppercase_data = {}
    filtered_data = {}

    for key, value in data.items():
        has_underscore = key in underscore_keys
        is_uppercase = key in uppercase_keys

        if has_underscore:
            underscore_data[key] = value

        if is_uppercase:
            uppercase_data[key] = value

        if not has_underscore and not is_uppercase:
            filtered_data[key] = value

    return underscore_data, uppercase_data, filtered_data


def main():
    parser = argparse.ArgumentParser(
        description="Separate flattened JSON into underscore keys, uppercase values, and filtered versions"
    )
    parser.add_argument("flat_json", help="Primary flattened JSON file (used to determine categories)")
    parser.add_argument(
        "--language-files",
        default="",
        help="Comma-separated list of additional language files to filter (e.g., './output/flat/fr.flat.json,./output/flat/nl.flat.json')",
    )
    parser.add_argument(
        "--underscore-out",
        default="flat_underscore.json",
        help="Output file for keys containing underscore (suffix for language files)",
    )
    parser.add_argument(
        "--uppercase-out",
        default="flat_uppercase.json",
        help="Output file for all-uppercase values (suffix for language files)",
    )
    parser.add_argument(
        "--filtered-out",
        default="flat_filtered.json",
        help="Output file without underscore and uppercase (suffix for language files)",
    )

    args = parser.parse_args()

    flat_path = Path(args.flat_json)

    if not flat_path.exists():
        parser.error(f"Flat JSON file not found: {flat_path}")

    log(f"Loading primary flattened JSON: {flat_path}")
    with open(flat_path, encoding="utf-8") as f:
        data = json.load(f)

    original_count = len(data)
    log(f"Loaded {original_count} keys")

    # Determine underscore and uppercase key sets from primary file
    underscore_keys = set()
    uppercase_keys = set()

    for key, value in data.items():
        str_value = str(value)
        if '_' in key:
            underscore_keys.add(key)
        if is_all_uppercase(str_value):
            uppercase_keys.add(key)

    log(f"Found {len(underscore_keys)} keys with underscore")
    log(f"Found {len(uppercase_keys)} keys with uppercase values")

    # Process primary file
    underscore_data, uppercase_data, filtered_data = separate_file(data, underscore_keys, uppercase_keys)

    # Write primary file outputs
    underscore_out = Path(args.underscore_out)
    uppercase_out = Path(args.uppercase_out)
    filtered_out = Path(args.filtered_out)

    log(f"Writing underscore keys to: {underscore_out}")
    with open(underscore_out, "w", encoding="utf-8") as f:
        json.dump(underscore_data, f, ensure_ascii=False, indent=2)
    log(f"Wrote {len(underscore_data)} underscore keys")

    log(f"Writing uppercase values to: {uppercase_out}")
    with open(uppercase_out, "w", encoding="utf-8") as f:
        json.dump(uppercase_data, f, ensure_ascii=False, indent=2)
    log(f"Wrote {len(uppercase_data)} uppercase keys")

    log(f"Writing filtered keys to: {filtered_out}")
    with open(filtered_out, "w", encoding="utf-8") as f:
        json.dump(filtered_data, f, ensure_ascii=False, indent=2)
    log(f"Wrote {len(filtered_data)} filtered keys")

    # Process additional language files if provided
    if args.language_files:
        lang_files = [p.strip() for p in args.language_files.split(",")]
        log(f"\nProcessing {len(lang_files)} additional language file(s)...")

        for lang_file in lang_files:
            lang_path = Path(lang_file)
            if not lang_path.exists():
                log(f"⚠️  Language file not found: {lang_path}")
                continue

            log(f"\nLoading language file: {lang_path}")
            with open(lang_path, encoding="utf-8") as f:
                lang_data = json.load(f)

            lang_count = len(lang_data)
            log(f"Loaded {lang_count} keys")

            # Separate using the same categories from primary file
            lang_underscore, lang_uppercase, lang_filtered = separate_file(lang_data, underscore_keys, uppercase_keys)

            # Generate output paths based on input file name
            stem = lang_path.stem  # e.g., "fr.flat"
            parent = lang_path.parent

            lang_underscore_out = parent / f"{stem}.underscore.json"
            lang_uppercase_out = parent / f"{stem}.uppercase.json"
            lang_filtered_out = parent / f"{stem}.filtered.json"

            log(f"Writing to: {lang_underscore_out}")
            with open(lang_underscore_out, "w", encoding="utf-8") as f:
                json.dump(lang_underscore, f, ensure_ascii=False, indent=2)
            log(f"Wrote {len(lang_underscore)} underscore keys")

            log(f"Writing to: {lang_uppercase_out}")
            with open(lang_uppercase_out, "w", encoding="utf-8") as f:
                json.dump(lang_uppercase, f, ensure_ascii=False, indent=2)
            log(f"Wrote {len(lang_uppercase)} uppercase keys")

            log(f"Writing to: {lang_filtered_out}")
            with open(lang_filtered_out, "w", encoding="utf-8") as f:
                json.dump(lang_filtered, f, ensure_ascii=False, indent=2)
            log(f"Wrote {len(lang_filtered)} filtered keys")

            # Validate counts
            overlap = len([k for k in lang_underscore if k in lang_uppercase])
            total = len(lang_underscore) + len(lang_uppercase) + len(lang_filtered) - overlap
            if total == lang_count:
                log(f"✓ Validation passed for {lang_path.name}")
            else:
                log(f"✗ Validation FAILED for {lang_path.name}: expected {lang_count}, got {total}")

    # Validation for primary file: Check total counts
    total_separated = len(underscore_data) + len(uppercase_data) + len(filtered_data)

    # Account for keys that might be in multiple categories (underscore + uppercase)
    overlap_count = len([k for k in underscore_data if k in uppercase_data])
    adjusted_total = total_separated - overlap_count

    log("")
    log("=" * 60)
    log("PRIMARY FILE SUMMARY:")
    log("=" * 60)
    log(f"Original keys: {original_count}")
    log(f"Keys with underscore: {len(underscore_data)}")
    log(f"Keys with uppercase values: {len(uppercase_data)}")
    log(f"Keys with both underscore & uppercase: {overlap_count}")
    log(f"Filtered keys (safe): {len(filtered_data)}")
    log(f"Total unique keys: {adjusted_total}")
    log("=" * 60)

    # Validate
    if adjusted_total == original_count:
        log("✓ VALIDATION PASSED: Total keys match original")
        return 0
    else:
        log(f"✗ VALIDATION FAILED: Expected {original_count}, got {adjusted_total}")
        log(f"  Difference: {adjusted_total - original_count}")
        return 1


if __name__ == "__main__":
    exit(main())
