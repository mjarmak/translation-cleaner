import json
import argparse
import sys
from pathlib import Path

def log(msg: str):
    print(f"[validate-remap] {msg}")

def main():
    parser = argparse.ArgumentParser(
        description="Validate that all keys in a remapped JSON file exist in the mapping file's mapKeyTo/mapValueTo"
    )

    parser.add_argument("remapped_json", help="Remapped JSON file to validate")
    parser.add_argument("mapping_json", help="Mapping JSON file used for remapping")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show missing keys in detail",
    )

    args = parser.parse_args()

    remapped_path = Path(args.remapped_json)
    mapping_path = Path(args.mapping_json)

    if not remapped_path.exists():
        log(f"❌ Remapped JSON file not found: {remapped_path}")
        sys.exit(1)

    if not mapping_path.exists():
        log(f"❌ Mapping JSON file not found: {mapping_path}")
        sys.exit(1)

    log(f"Loading remapped JSON: {remapped_path}")
    with open(remapped_path, encoding="utf-8") as f:
        remapped_data = json.load(f)

    log(f"Loading mapping JSON: {mapping_path}")
    with open(mapping_path, encoding="utf-8") as f:
        mapping_data = json.load(f)

    if not isinstance(remapped_data, dict):
        log(f"❌ Invalid remapped JSON structure: expected dict, got {type(remapped_data).__name__}")
        sys.exit(1)

    if not isinstance(mapping_data, list):
        log(f"❌ Invalid mapping JSON structure: expected list, got {type(mapping_data).__name__}")
        sys.exit(1)

    # Extract all keys from remapped JSON (flattened)
    def extract_all_keys(obj, prefix=""):
        """Recursively extract all keys from nested object"""
        keys = set()
        if isinstance(obj, dict):
            for key, value in obj.items():
                full_key = f"{prefix}{key}" if prefix else key
                keys.add(full_key)
                if isinstance(value, dict):
                    keys.update(extract_all_keys(value, f"{full_key}."))
        return keys

    remapped_keys = extract_all_keys(remapped_data)
    log(f"Remapped JSON contains {len(remapped_keys)} keys")

    # Build set of mapKeyTo values from mapping
    mapped_keys = set()
    for entry in mapping_data:
        if not isinstance(entry, dict):
            log(f"❌ Invalid entry in mapping: expected dict, got {type(entry).__name__}")
            sys.exit(1)

        map_key_to = entry.get("mapKeyTo")
        if map_key_to:
            mapped_keys.add(map_key_to)

    log(f"Mapping JSON contains {len(mapped_keys)} unique mapKeyTo values")

    # Find keys in remapped JSON that are NOT in mapping's mapKeyTo
    missing_in_mapping = remapped_keys - mapped_keys

    if missing_in_mapping:
        log(f"\n❌ Validation FAILED: Found {len(missing_in_mapping)} keys in remapped JSON that don't exist in mapping's mapKeyTo:")

        if args.verbose:
            for key in sorted(missing_in_mapping)[:30]:
                log(f"   - {key}")
            if len(missing_in_mapping) > 30:
                log(f"   ... and {len(missing_in_mapping) - 30} more")
        else:
            log(f"   Use --verbose to see the missing keys")

        sys.exit(1)
    else:
        log(f"✅ Validation PASSED:")
        log(f"   • All {len(remapped_keys)} keys in remapped JSON exist in mapping's mapKeyTo")
        log(f"   • No orphaned keys detected")
        sys.exit(0)

if __name__ == "__main__":
    main()
