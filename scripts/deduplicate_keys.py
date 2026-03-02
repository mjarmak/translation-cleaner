import json
import argparse
import base64
from collections import defaultdict
from pathlib import Path


def log(msg: str):
    print(f"[i18n-dedupe] {msg}")


def to_base64(value: str) -> str:
    """
    URL-safe base64 without padding.
    """
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

    args = parser.parse_args()

    flat_path = Path(args.flat_json)
    duplicates_out = Path(args.duplicates_out)
    mapping_out = Path(args.mapping_out)

    if not flat_path.exists():
        raise FileNotFoundError(f"Flatten file not found: {flat_path}")

    log(f"Loading flattened file: {flat_path}")

    with open(flat_path, encoding="utf-8") as f:
        data = json.load(f)

    log(f"Loaded {len(data)} total keys")

    # Group keys by value
    value_to_keys = defaultdict(list)

    for key, value in data.items():
        value_to_keys[str(value)].append(key)

    # Filter duplicates only
    duplicates = {
        value: keys
        for value, keys in value_to_keys.items()
        if len(keys) > 1
    }

    log(f"Found {len(duplicates)} duplicated values")

    # -------------------------------------------------
    # Write duplicates listing
    # -------------------------------------------------
    log(f"Writing duplicates list to: {duplicates_out}")

    with open(duplicates_out, "w", encoding="utf-8") as f:
        for value, keys in duplicates.items():
            f.write(f"VALUE: {value}\n")
            for k in keys:
                f.write(f"  - {k}\n")
            f.write("\n")

    # -------------------------------------------------
    # Write base64 mapping
    # -------------------------------------------------
    log(f"Writing base64 mapping to: {mapping_out}")

    total_mapped = 0

    with open(mapping_out, "w", encoding="utf-8") as f:
        for value, keys in duplicates.items():
            hash_key = to_base64(value)

            for k in keys:
                f.write(f"{hash_key}: {k}\n")
                total_mapped += 1

    log(f"Wrote {total_mapped} base64 key mappings")

    log("✅ Done")


if __name__ == "__main__":
    main()