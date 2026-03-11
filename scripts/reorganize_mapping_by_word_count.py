import json
import argparse
from pathlib import Path


def log(msg: str):
    print(f"[reorganize-mapping] {msg}")


def count_words(text: str) -> int:
    """Count the number of words in a text"""
    return len(text.split())


def reorganize_mapping(mapping_json_path: str, output_path: str = None):
    """
    Reorganize mapping file by moving keys with values below 6 words to i18n.common
    Ignores keys that are already under i18n namespace
    """
    mapping_path = Path(mapping_json_path)

    if not mapping_path.exists():
        log(f"✗ Mapping file not found: {mapping_path}")
        return 1

    log(f"Loading mapping JSON: {mapping_path}")
    with open(mapping_path, encoding="utf-8") as f:
        mapping_array = json.load(f)

    log(f"Loaded {len(mapping_array)} mapping entries")

    moved_count = 0
    short_value_entries = []
    long_value_entries = []

    for entry in mapping_array:
        value = entry.get("value", "")
        word_count = count_words(value)
        map_key_to = entry.get("mapKeyTo", "")

        # Check if already under i18n namespace
        already_in_i18n = map_key_to.startswith("i18n.common") or map_key_to.startswith("i18n.")

        if word_count < 6 and not already_in_i18n:
            # Move to i18n.common
            # Extract the last part of the original key for the new key
            keys = entry.get("keys", [])
            if keys:
                original_key = keys[0].get("key", "")
                # Use the last part of the key
                key_parts = original_key.split(".")
                last_part = key_parts[-1]

                # Create new mapKeyTo
                new_map_key_to = f"i18n.common.{last_part}"
                entry["mapKeyTo"] = new_map_key_to
                moved_count += 1

                log(f"  Moved: {value!r} ({word_count} words) → {new_map_key_to}")

            short_value_entries.append(entry)
        else:
            long_value_entries.append(entry)

    # Save updated mapping
    output_file = Path(output_path) if output_path else mapping_path
    log(f"\nSaving reorganized mapping to: {output_file}")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(short_value_entries + long_value_entries, f, indent=2, ensure_ascii=False)

    # Summary
    log("")
    log("=" * 60)
    log("REORGANIZE MAPPING SUMMARY:")
    log("=" * 60)
    log(f"Total entries: {len(mapping_array)}")
    log(f"Entries moved to i18n.common: {moved_count}")
    log(f"Entries with short values (< 6 words): {len(short_value_entries)}")
    log(f"Entries with long values (≥ 6 words): {len(long_value_entries)}")
    log("=" * 60)
    log("✅ Done")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Reorganize mapping file by moving keys with short values to i18n.common"
    )
    parser.add_argument(
        "mapping_json",
        help="Canonical mapping JSON file from canonical_map.py"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: overwrite input file)"
    )

    args = parser.parse_args()

    return reorganize_mapping(args.mapping_json, args.output)


if __name__ == "__main__":
    exit(main())
