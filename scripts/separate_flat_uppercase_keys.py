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


def main():
    parser = argparse.ArgumentParser(
        description="Separate English flat JSON into underscore, uppercase, and filtered versions. Generate only filtered versions for other languages."
    )
    parser.add_argument("flat_json", help="Primary English flattened JSON file")
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Output directory for all separated files",
    )
    parser.add_argument(
        "--language-files",
        default="",
        help="Comma-separated list of additional language files to filter (e.g., './output/flat/fr.flat.json,./output/flat/nl.flat.json')",
    )

    args = parser.parse_args()

    flat_path = Path(args.flat_json)
    output_dir = Path(args.output_dir)

    if not flat_path.exists():
        parser.error(f"Flat JSON file not found: {flat_path}")

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    log(f"Output directory: {output_dir}")

    log(f"Loading English flattened JSON: {flat_path}")
    with open(flat_path, encoding="utf-8") as f:
        data = json.load(f)

    original_count = len(data)
    log(f"Loaded {original_count} keys")

    # Determine underscore and uppercase key sets from English file
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

    # Separate English file into three categories
    underscore_data = {}
    uppercase_data = {}
    filtered_data = {}

    for key, value in data.items():
        if key in underscore_keys:
            underscore_data[key] = value

        if key in uppercase_keys:
            uppercase_data[key] = value

        if key not in underscore_keys and key not in uppercase_keys:
            filtered_data[key] = value

    # Generate English output paths
    en_stem = flat_path.stem  # e.g., "en.flat"
    underscore_out = output_dir / f"{en_stem}.underscore.json"
    uppercase_out = output_dir / f"{en_stem}.uppercase.json"
    filtered_out = output_dir / f"{en_stem}.filtered.json"

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

    # Process additional language files - generate all 3 files
    if args.language_files:
        lang_files = [p.strip() for p in args.language_files.split(",")]
        log(f"\nProcessing {len(lang_files)} additional language file(s) - generating all 3 files...")

        for lang_file in lang_files:
            lang_path = Path(lang_file)
            if not lang_path.exists():
                log(f"⚠️  Language file not found: {lang_path}")
                continue

            log(f"\nLoading: {lang_path}")
            with open(lang_path, encoding="utf-8") as f:
                lang_data = json.load(f)

            lang_count = len(lang_data)
            log(f"Loaded {lang_count} keys")

            # Create all three separated categories (use same categories as English)
            lang_underscore = {k: v for k, v in lang_data.items() if k in underscore_keys}
            lang_uppercase = {k: v for k, v in lang_data.items() if k in uppercase_keys}
            lang_filtered = {k: v for k, v in lang_data.items() if k not in underscore_keys and k not in uppercase_keys}

            # Generate output paths
            lang_stem = lang_path.stem  # e.g., "fr.flat"
            lang_underscore_out = output_dir / f"{lang_stem}.underscore.json"
            lang_uppercase_out = output_dir / f"{lang_stem}.uppercase.json"
            lang_filtered_out = output_dir / f"{lang_stem}.filtered.json"

            log(f"Writing underscore keys to: {lang_underscore_out}")
            with open(lang_underscore_out, "w", encoding="utf-8") as f:
                json.dump(lang_underscore, f, ensure_ascii=False, indent=2)
            log(f"Wrote {len(lang_underscore)} underscore keys")

            log(f"Writing uppercase values to: {lang_uppercase_out}")
            with open(lang_uppercase_out, "w", encoding="utf-8") as f:
                json.dump(lang_uppercase, f, ensure_ascii=False, indent=2)
            log(f"Wrote {len(lang_uppercase)} uppercase keys")

            log(f"Writing filtered keys to: {lang_filtered_out}")
            with open(lang_filtered_out, "w", encoding="utf-8") as f:
                json.dump(lang_filtered, f, ensure_ascii=False, indent=2)
            log(f"Wrote {len(lang_filtered)} filtered keys")

            # Validate
            overlap = len([k for k in lang_underscore if k in lang_uppercase])
            total = len(lang_underscore) + len(lang_uppercase) + len(lang_filtered) - overlap
            if total == lang_count:
                log(f"✓ Validation passed for {lang_path.name}")
            else:
                log(f"✗ Validation FAILED for {lang_path.name}: expected {lang_count}, got {total}")

    # Validation for English file: Check total counts
    total_separated = len(underscore_data) + len(uppercase_data) + len(filtered_data)
    overlap_count = len([k for k in underscore_data if k in uppercase_data])
    adjusted_total = total_separated - overlap_count

    log("")
    log("=" * 60)
    log("ENGLISH FILE SUMMARY:")
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
