import json
import argparse
import base64
from collections import defaultdict
from pathlib import Path

def log(msg: str):
    print(f"[i18n-dedupe] {msg}")

def to_base64(value: str) -> str:
    """URL-safe base64 without padding."""
    return base64.urlsafe_b64encode(value.encode("utf-8")).decode("ascii").rstrip("=")

def main():
    parser = argparse.ArgumentParser(
        description="Find duplicated translation values and generate base64 mapping"
    )

    parser.add_argument("flat_json", help="Flattened i18n JSON file")
    parser.add_argument(
        "--duplicates-out",
        default="duplicates.txt",
        help="Output file listing duplicated values and their keys",
    )
    parser.add_argument(
        "--mapping-out",
        default="hash_mapping.txt",
        help="Output file mapping base64(value) to original keys",
    )
    parser.add_argument(
        "--prefix",
        default="",
        help="Optional prefix to prepend to each base64 hash in the mapping file",
    )
    parser.add_argument(
        "--ignore-case",
        action="store_true",
        help="Case-insensitive duplicate detection",
    )

    args = parser.parse_args()

    flat_path = Path(args.flat_json)
    duplicates_out = Path(args.duplicates_out)
    mapping_out = Path(args.mapping_out)
    prefix = args.prefix
    ignore_case = args.ignore_case

    if not flat_path.exists():
        raise FileNotFoundError(f"Flatten file not found: {flat_path}")

    log(f"Loading flattened file: {flat_path}")
    log(f"Case insensitive mode: {'ON' if ignore_case else 'OFF'}")
    with open(flat_path, encoding="utf-8") as f:
        data = json.load(f)

    log(f"Loaded {len(data)} total keys")

    # Group keys by value
    value_to_keys = defaultdict(list)
    for key, value in data.items():
        str_value = str(value)
        # Use lowercase value as the grouping key if ignore_case is True
        group_key = str_value.lower() if ignore_case else str_value
        value_to_keys[group_key].append((str_value, key))

    # Filter duplicates only
    duplicates = {value: keys for value, keys in value_to_keys.items() if len(keys) > 1}
    log(f"Found {len(duplicates)} duplicated values")

    # -------------------------------------------------
    # Write duplicates listing
    # -------------------------------------------------
    log(f"Writing duplicates list to: {duplicates_out}")

    # Calculate statistics
    total_duplicate_keys = sum(len(keys) for keys in duplicates.values())
    total_unique_values = len(duplicates)

    with open(duplicates_out, "w", encoding="utf-8") as f:
        # Write summary header
        f.write("=" * 60 + "\n")
        f.write("DUPLICATES REPORT SUMMARY\n")
        f.write("=" * 60 + "\n")
        f.write(f"Total duplicate values found: {total_unique_values}\n")
        f.write(f"Total duplicate keys found: {total_duplicate_keys}\n")
        f.write(f"Unique values with 2+ keys: {total_unique_values}\n")
        f.write("=" * 60 + "\n\n")

        for value_key, key_list in duplicates.items():
            # Extract original value from first tuple
            original_value = key_list[0][0]
            f.write(f"VALUE: {original_value}\n")
            for value, k in key_list:
                f.write(f"  - {k} = {value}\n")
            f.write("\n")

    # -------------------------------------------------
    # Write base64 mapping with optional prefix
    # -------------------------------------------------
    log(f"Writing base64 mapping to: {mapping_out}")
    total_mapped = 0
    with open(mapping_out, "w", encoding="utf-8") as f:
        for value_key, key_list in duplicates.items():
            # Use original value for hash generation
            original_value = key_list[0][0]
            hash_key = prefix + to_base64(original_value)
            for _, k in key_list:
                f.write(f"{hash_key}: {k}\n")
                total_mapped += 1

    log(f"Wrote {total_mapped} base64 key mappings")
    log("✅ Done")

if __name__ == "__main__":
    main()