import json
import argparse
from pathlib import Path


def log(msg: str):
    print(f"[i18n-apply] {msg}")


def main():
    parser = argparse.ArgumentParser(
        description="Apply canonical mapping to flat JSON file - rename keys and optionally values"
    )
    parser.add_argument(
        "flat_json",
        help="Flattened JSON file to apply mapping to"
    )
    parser.add_argument(
        "mapping_json",
        help="Canonical mapping JSON file from canonical_map.py"
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Output file with applied mapping"
    )
    parser.add_argument(
        "--mapValues",
        action="store_true",
        help="Also replace values with mapValueTo (recommended for English only)"
    )

    args = parser.parse_args()

    flat_path = Path(args.flat_json)
    mapping_path = Path(args.mapping_json)
    output_path = Path(args.out)
    map_values = args.mapValues

    if not flat_path.exists():
        parser.error(f"Flat JSON file not found: {flat_path}")

    if not mapping_path.exists():
        parser.error(f"Mapping JSON file not found: {mapping_path}")

    # Create output directory if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)

    log(f"Loading flat JSON: {flat_path}")
    with open(flat_path, encoding="utf-8") as f:
        flat_data = json.load(f)

    log(f"Loading mapping JSON: {mapping_path}")
    with open(mapping_path, encoding="utf-8") as f:
        mapping_array = json.load(f)

    log(f"Loaded {len(flat_data)} keys from flat JSON")
    log(f"Loaded {len(mapping_array)} mapping entries")

    # Build mapping dictionaries from the array
    # mapping: old_key -> new_key (mapKeyTo)
    # value_mapping: old_value -> new_value (mapValueTo)
    key_mapping = {}
    value_mapping = {}

    for entry in mapping_array:
        original_value = entry["value"]
        map_key_to = entry["mapKeyTo"]
        map_value_to = entry["mapValueTo"]

        # Map all keys in this group to the mapKeyTo
        for key_entry in entry["keys"]:
            old_key = key_entry["key"]
            key_mapping[old_key] = map_key_to

        # Map all values to mapValueTo (for case-insensitive matching)
        # Store value mappings for both case-sensitive and variations
        for key_entry in entry["keys"]:
            old_value = key_entry["value"]
            # Map the exact value
            if old_value not in value_mapping:
                value_mapping[old_value] = map_value_to

    log(f"Built mapping for {len(key_mapping)} keys")
    log(f"Built mapping for {len(value_mapping)} values")

    # Apply mapping to flat data
    mapped_data = {}
    keys_renamed = 0
    values_mapped = 0
    keys_not_found = 0

    for old_key, old_value in flat_data.items():
        str_value = str(old_value)

        # Determine new key
        if old_key in key_mapping:
            new_key = key_mapping[old_key]
            keys_renamed += 1
        else:
            new_key = old_key
            keys_not_found += 1

        # Determine new value
        if map_values and str_value in value_mapping:
            new_value = value_mapping[str_value]
            values_mapped += 1
        else:
            new_value = old_value

        # Handle duplicate keys - if key already exists, skip or warn
        if new_key in mapped_data:
            log(f"⚠️  Warning: Key collision - '{new_key}' already exists (from '{old_key}')")
        else:
            mapped_data[new_key] = new_value

    # Write output
    log(f"Writing mapped JSON to: {output_path}")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(mapped_data, f, ensure_ascii=False, indent=2)

    # Summary
    log("")
    log("=" * 60)
    log("MAPPING SUMMARY:")
    log("=" * 60)
    log(f"Keys renamed: {keys_renamed}")
    log(f"Keys not in mapping (unchanged): {keys_not_found}")
    if map_values:
        log(f"Values mapped: {values_mapped}")
    else:
        log("Values mapping: DISABLED (use --mapValues to enable)")
    log(f"Total keys in output: {len(mapped_data)}")
    log("=" * 60)
    log("✅ Done")

    return 0


if __name__ == "__main__":
    exit(main())
