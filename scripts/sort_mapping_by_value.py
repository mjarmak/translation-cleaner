import json
import argparse
from pathlib import Path


def log(msg: str):
    print(f"[sort-mapping] {msg}")


def sort_mapping_by_value(mapping_json_path: str, output_path: str = None):
    """
    Sort mapping JSON file by the 'value' field alphabetically
    """
    mapping_path = Path(mapping_json_path)

    if not mapping_path.exists():
        log(f"✗ Mapping file not found: {mapping_path}")
        return 1

    log(f"Loading mapping JSON: {mapping_path}")
    with open(mapping_path, encoding="utf-8") as f:
        mapping_array = json.load(f)

    log(f"Loaded {len(mapping_array)} mapping entries")

    # Sort by value field
    sorted_mapping = sorted(mapping_array, key=lambda x: x.get("value", "").lower())

    log(f"Sorted {len(sorted_mapping)} entries alphabetically by value")

    # Save sorted mapping
    output_file = Path(output_path) if output_path else mapping_path
    log(f"Writing sorted mapping to: {output_file}")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(sorted_mapping, f, indent=2, ensure_ascii=False)

    # Summary
    log("")
    log("=" * 60)
    log("SORT MAPPING SUMMARY:")
    log("=" * 60)
    log(f"Total entries sorted: {len(sorted_mapping)}")
    log(f"Sorted by: value field (case-insensitive)")
    log(f"Output file: {output_file}")
    log("=" * 60)
    log("✅ Done")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Sort mapping JSON file by the 'value' field alphabetically"
    )
    parser.add_argument(
        "mapping_json",
        help="Mapping JSON file to sort"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: overwrite input file)"
    )

    args = parser.parse_args()

    return sort_mapping_by_value(args.mapping_json, args.output)


if __name__ == "__main__":
    exit(main())
