import json
import argparse
import sys
from pathlib import Path

def log(msg: str):
    print(f"[validate-coverage] {msg}")

def main():
    parser = argparse.ArgumentParser(
        description="Validate that the mapping file contains all keys from the flat JSON file"
    )

    parser.add_argument("flat_json", help="Flattened i18n JSON file")
    parser.add_argument("mapping_json", help="Mapping JSON file")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show missing keys in detail",
    )

    args = parser.parse_args()

    flat_path = Path(args.flat_json)
    mapping_path = Path(args.mapping_json)

    if not flat_path.exists():
        log(f"❌ Flat JSON file not found: {flat_path}")
        sys.exit(1)

    if not mapping_path.exists():
        log(f"❌ Mapping JSON file not found: {mapping_path}")
        sys.exit(1)

    log(f"Loading flat JSON: {flat_path}")
    with open(flat_path, encoding="utf-8") as f:
        flat_data = json.load(f)

    log(f"Loading mapping JSON: {mapping_path}")
    with open(mapping_path, encoding="utf-8") as f:
        mapping_data = json.load(f)

    if not isinstance(flat_data, dict):
        log(f"❌ Invalid flat JSON structure: expected dict, got {type(flat_data).__name__}")
        sys.exit(1)

    if not isinstance(mapping_data, list):
        log(f"❌ Invalid mapping JSON structure: expected list, got {type(mapping_data).__name__}")
        sys.exit(1)

    flat_keys = set(flat_data.keys())
    log(f"Flat JSON contains {len(flat_keys)} keys")

    # Collect all keys from the mapping file
    mapping_keys = set()
    for entry in mapping_data:
        if not isinstance(entry, dict):
            log(f"❌ Invalid entry in mapping: expected dict, got {type(entry).__name__}")
            sys.exit(1)

        if "keys" not in entry:
            log(f"❌ Missing 'keys' field in mapping entry with value '{entry.get('value', 'N/A')}'")
            sys.exit(1)

        keys_array = entry["keys"]
        if not isinstance(keys_array, list):
            log(f"❌ Invalid 'keys' field: expected list, got {type(keys_array).__name__}")
            sys.exit(1)

        for key_entry in keys_array:
            if isinstance(key_entry, dict) and "key" in key_entry:
                mapping_keys.add(key_entry["key"])

    log(f"Mapping JSON contains {len(mapping_keys)} keys")

    # Compare
    missing_in_mapping = flat_keys - mapping_keys
    extra_in_mapping = mapping_keys - flat_keys

    # Validate that all keys in mapping actually exist in flat JSON
    invalid_keys_in_mapping = []
    for entry in mapping_data:
        keys_array = entry.get("keys", [])
        for key_entry in keys_array:
            if isinstance(key_entry, dict) and "key" in key_entry:
                key = key_entry["key"]
                if key not in flat_keys:
                    invalid_keys_in_mapping.append({
                        "key": key,
                        "value": entry.get("value", "N/A"),
                        "mapKeyTo": entry.get("mapKeyTo", "N/A")
                    })

    validation_errors = bool(missing_in_mapping or extra_in_mapping or invalid_keys_in_mapping)

    if validation_errors:
        log(f"\n❌ Validation FAILED: Key mismatch detected")

        if missing_in_mapping:
            log(f"\n⚠️  Missing in mapping ({len(missing_in_mapping)} keys):")
            if args.verbose:
                for key in sorted(missing_in_mapping)[:20]:
                    log(f"   - {key}")
                if len(missing_in_mapping) > 20:
                    log(f"   ... and {len(missing_in_mapping) - 20} more")
            else:
                log(f"   Use --verbose to see the missing keys")

        if extra_in_mapping:
            log(f"\n⚠️  Extra in mapping ({len(extra_in_mapping)} keys):")
            if args.verbose:
                for key in sorted(extra_in_mapping)[:20]:
                    log(f"   - {key}")
                if len(extra_in_mapping) > 20:
                    log(f"   ... and {len(extra_in_mapping) - 20} more")
            else:
                log(f"   Use --verbose to see the extra keys")

        if invalid_keys_in_mapping:
            log(f"\n❌ Invalid keys in mapping ({len(invalid_keys_in_mapping)} keys) - NOT FOUND in flat JSON:")
            if args.verbose:
                for invalid_entry in invalid_keys_in_mapping[:20]:
                    log(f"   - Key: {invalid_entry['key']}")
                    log(f"     Value: {invalid_entry['value']}")
                    log(f"     MapsTo: {invalid_entry['mapKeyTo']}")
                if len(invalid_keys_in_mapping) > 20:
                    log(f"   ... and {len(invalid_keys_in_mapping) - 20} more")
            else:
                log(f"   Use --verbose to see the invalid keys")

        sys.exit(1)
    else:
        log(f"✅ Validation PASSED:")
        log(f"   • All {len(flat_keys)} keys from flat JSON are covered in the mapping")
        log(f"   • All {len(mapping_keys)} keys in mapping exist in the flat JSON")
        log(f"   • No orphaned or invalid keys detected")
        sys.exit(0)

if __name__ == "__main__":
    main()
