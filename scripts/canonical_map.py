import json
import argparse
import hashlib
import base64
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

def is_pascal_case(value: str) -> bool:
    """Check if value is in PascalCase (every word begins with uppercase)."""
    if not value:
        return False
    # Split by spaces and check each word
    words = value.split()
    if not words:
        return False
    # Each word should start with uppercase
    for word in words:
        # Remove non-letter characters at the start to check first letter
        first_letter_found = False
        for char in word:
            if char.isalpha():
                if not char.isupper():
                    return False
                first_letter_found = True
                break
        if not first_letter_found:
            return False
    return True

def generate_hash_suffix(value: str) -> str:
    """Generate a short base64 hash suffix for a value."""
    hash_obj = hashlib.md5(value.encode())
    hash_bytes = hash_obj.digest()[:6]  # Take first 6 bytes for shorter hash
    hash_b64 = base64.b64encode(hash_bytes).decode().rstrip('=')  # Remove padding
    return 'hash_' + hash_b64

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

    # Separate keys that are already in i18n namespace
    i18n_keys = {}
    non_i18n_keys = {}

    for key, value in data.items():
        if key.startswith("i18n."):
            i18n_keys[key] = value
        else:
            non_i18n_keys[key] = value

    log(f"Found {len(i18n_keys)} keys already in i18n namespace (will not be merged)")
    log(f"Found {len(non_i18n_keys)} keys outside i18n namespace (will be deduplicated)")

    # Group keys by value (only non-i18n keys)
    value_to_keys = defaultdict(list)
    for key, value in non_i18n_keys.items():
        str_value = str(value)
        # Use lowercase value as the grouping key if ignore_case is True
        group_key = str_value.lower() if ignore_case else str_value
        value_to_keys[group_key].append((str_value, key))

    # Separate duplicates and non-duplicates
    duplicates = {value: keys for value, keys in value_to_keys.items() if len(keys) > 1}
    non_duplicates = {value: keys for value, keys in value_to_keys.items() if len(keys) == 1}
    log(f"Found {len(duplicates)} duplicated values")
    log(f"Found {len(non_duplicates)} unique values")

    # -------------------------------------------------
    # Build JSON structure (all entries)
    # -------------------------------------------------
    all_entries_array = []
    map_to_tracker = defaultdict(list)  # Track which entries use which mapKeyTo

    # First pass: create duplicate objects and track mapKeyTo usage
    for value_key, key_list in duplicates.items():
        # Extract original value from first tuple
        original_value = key_list[0][0]
        last_word = extract_last_word(key_list[0][1])  # Last word after '.' from first key
        map_to = prefix + last_word  # Apply prefix to mapTo

        # Find PascalCase value from all values in this duplicate group
        map_value_to = None
        for value, k in key_list:
            if is_pascal_case(value):
                map_value_to = value
                break
        # If no PascalCase value found, use the original value
        if not map_value_to:
            map_value_to = original_value

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
            "mapKeyTo": map_to,
            "mapValueTo": map_value_to,
            "keys": keys_array
        }

        all_entries_array.append(duplicate_obj)
        map_to_tracker[map_to].append(duplicate_obj)

    # Second pass: add non-duplicate entries (count = 1)
    for value_key, key_list in non_duplicates.items():
        original_value = key_list[0][0]
        key = key_list[0][1]

        # For non-duplicates, mapKeyTo is just the key itself
        map_to = key

        # For non-duplicates, mapValueTo is the value itself
        map_value_to = original_value

        # Build keys array with single entry
        keys_array = [{
            "key": key,
            "value": original_value
        }]

        # Build entry object
        entry_obj = {
            "value": original_value,
            "count": 1,
            "mapKeyTo": map_to,
            "mapValueTo": map_value_to,
            "keys": keys_array
        }

        all_entries_array.append(entry_obj)

    # Third pass: add i18n namespace keys as non-mergeable entries
    for key, value in i18n_keys.items():
        original_value = str(value)

        # For i18n keys, mapKeyTo and mapValueTo remain the same (no remapping)
        map_to = key
        map_value_to = original_value

        # Build keys array with single entry
        keys_array = [{
            "key": key,
            "value": original_value
        }]

        # Build entry object
        entry_obj = {
            "value": original_value,
            "count": 1,
            "mapKeyTo": map_to,
            "mapValueTo": map_value_to,
            "keys": keys_array
        }

        all_entries_array.append(entry_obj)

    # Fourth pass: resolve mapKeyTo conflicts by adding hash suffix (only for duplicates)
    for map_key, entries in map_to_tracker.items():
        if len(entries) > 1:  # Conflict detected
            for i, entry in enumerate(entries):
                # Generate hash suffix from the value
                hash_suffix = generate_hash_suffix(entry["value"])
                entry["mapKeyTo"] = f"{map_key}_{hash_suffix}"
                log(f"Resolved duplicate mapKeyTo '{map_key}' → '{entry['mapKeyTo']}' for value '{entry['value']}'")

    # Write JSON file
    log(f"Writing all entries JSON to: {duplicates_out}")
    with open(duplicates_out, "w", encoding="utf-8") as f:
        json.dump(all_entries_array, f, ensure_ascii=False, indent=2)

    duplicates_count = len(duplicates)
    non_duplicates_count = len(non_duplicates)
    i18n_count = len(i18n_keys)
    total_keys = sum(len(d['keys']) for d in all_entries_array)
    log(f"Wrote {len(all_entries_array)} total entries ({duplicates_count} duplicates, {non_duplicates_count} unique, {i18n_count} i18n) with {total_keys} total keys")
    log("✅ Done")

if __name__ == "__main__":
    main()

