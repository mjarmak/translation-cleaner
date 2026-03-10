import json
import argparse
import sys
from pathlib import Path
from collections import defaultdict

def log(msg: str):
    print(f"[validate-duplicates] {msg}")

def main():
    parser = argparse.ArgumentParser(
        description="Validate that there are no duplicate mapKeyTo values in the duplicates JSON file"
    )

    parser.add_argument("duplicates_json", help="Duplicates JSON file to validate")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed information about duplicates",
    )

    args = parser.parse_args()

    duplicates_path = Path(args.duplicates_json)

    if not duplicates_path.exists():
        log(f"❌ File not found: {duplicates_path}")
        sys.exit(1)

    log(f"Loading duplicates JSON: {duplicates_path}")
    with open(duplicates_path, encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        log(f"❌ Invalid JSON structure: expected list, got {type(data).__name__}")
        sys.exit(1)

    log(f"Loaded {len(data)} duplicate entries")

    # Track mapKeyTo values
    map_key_to_tracker = defaultdict(list)

    for idx, entry in enumerate(data):
        if not isinstance(entry, dict):
            log(f"❌ Invalid entry at index {idx}: expected dict, got {type(entry).__name__}")
            sys.exit(1)

        if "mapKeyTo" not in entry:
            log(f"❌ Missing 'mapKeyTo' field in entry {idx}")
            sys.exit(1)

        map_key_to = entry["mapKeyTo"]
        map_key_to_tracker[map_key_to].append(idx)

    # Check for duplicates
    duplicates_found = {k: v for k, v in map_key_to_tracker.items() if len(v) > 1}

    if duplicates_found:
        log(f"❌ Found {len(duplicates_found)} duplicate mapKeyTo values:")

        for map_key_to, indices in sorted(duplicates_found.items()):
            log(f"\n  mapKeyTo: '{map_key_to}'")
            log(f"  Found in {len(indices)} entries:")

            for idx in indices:
                entry = data[idx]
                value = entry.get("value", "N/A")
                count = entry.get("count", "N/A")
                if args.verbose:
                    log(f"    - Entry {idx}: value='{value}', count={count}")
                else:
                    log(f"    - Entry {idx}: value='{value}'")

        log("\n❌ Validation FAILED: Duplicate mapKeyTo values detected")
        sys.exit(1)
    else:
        log(f"✅ Validation PASSED: All {len(data)} mapKeyTo values are unique")
        sys.exit(0)

if __name__ == "__main__":
    main()
