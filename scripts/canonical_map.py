import json
import argparse
from collections import defaultdict
from pathlib import Path

def log(msg: str):
    print(f"[i18n-dedupe] {msg}")

def extract_last_word(key: str) -> str:
    """Extract the last word after the last dot (.) in a key."""
    parts = key.split('.')
    if parts:
        return parts[-1]
    return key

def main():
    parser = argparse.ArgumentParser(
        description="Find duplicated translation values and generate JSON duplicates file"
    )

    parser.add_argument("flat_json", help="Flattened i18n JSON file")
    parser.add_argument(
        "--duplicates-out",
        default="duplicates.json",
        help="Output file in JSON format listing duplicated values and their keys",
    )
    parser.add_argument(
        "--ignore-case",
        action="store_true",
        help="Case-insensitive duplicate detection",
    )
    parser.add_argument(
        "--prefix",
        default="",
        help="Prefix to prepend to all mapTo values",
    )

    args = parser.parse_args()

    flat_path = Path(args.flat_json)
    duplicates_out = Path(args.duplicates_out)
    ignore_case = args.ignore_case
    prefix = args.prefix

    if not flat_path.exists():
        parser.error(f"Flatten file not found: {flat_path}")

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
    # Build JSON duplicates structure
    # -------------------------------------------------
    duplicates_array = []

    for value_key, key_list in duplicates.items():
        # Extract original value from first tuple
        original_value = key_list[0][0]
        last_word = extract_last_word(key_list[0][1])  # Last word after '.' from first key
        map_to = prefix + last_word  # Apply prefix to mapTo

        # Build keys array
        keys_array = []
        for value, k in key_list:
            keys_array.append({
                "key": k,
                "value": value
            })

        # Build duplicate object
        duplicate_obj = {
            "value": original_value,
            "count": len(key_list),
            "mapTo": map_to,
            "keys": keys_array
        }

        duplicates_array.append(duplicate_obj)

    # Write JSON file
    log(f"Writing duplicates JSON to: {duplicates_out}")
    with open(duplicates_out, "w", encoding="utf-8") as f:
        json.dump(duplicates_array, f, ensure_ascii=False, indent=2)

    log(f"Wrote {len(duplicates_array)} duplicated values with {sum(len(d['keys']) for d in duplicates_array)} total keys")
    log("✅ Done")

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
