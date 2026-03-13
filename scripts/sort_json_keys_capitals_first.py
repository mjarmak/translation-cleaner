import json
import argparse
from pathlib import Path


def log(msg: str):
    print(f"[sort-json-keys] {msg}")


def starts_with_capital(text: str) -> bool:
    """Check if text starts with a capital letter"""
    if not text:
        return False
    return text[0].isupper()


def sort_json_keys_capitals_first(input_path: str, output_path: str = None):
    """
    Sort JSON file by keys, with keys starting with capital letters first.
    Preserves the nested structure of the JSON.
    """
    json_path = Path(input_path)

    if not json_path.exists():
        log(f"✗ JSON file not found: {json_path}")
        return 1

    log(f"Loading JSON file: {json_path}")
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        log(f"✗ Invalid JSON structure: expected dict, got {type(data).__name__}")
        return 1

    log(f"Loaded {len(data)} top-level keys")

    def sort_dict_keys(obj, depth=0):
        """Recursively sort dictionary keys, with capitals first"""
        if not isinstance(obj, dict):
            return obj

        # Separate keys into capital and non-capital
        capital_keys = []
        non_capital_keys = []

        for key in obj.keys():
            if starts_with_capital(key):
                capital_keys.append(key)
            else:
                non_capital_keys.append(key)

        # Sort each group alphabetically (case-insensitive)
        capital_keys.sort(key=str.lower)
        non_capital_keys.sort(key=str.lower)

        # Combine: capitals first, then others
        sorted_keys = capital_keys + non_capital_keys

        # Build sorted dictionary with recursively sorted values
        sorted_dict = {}
        for key in sorted_keys:
            value = obj[key]
            if isinstance(value, dict):
                sorted_dict[key] = sort_dict_keys(value, depth + 1)
            elif isinstance(value, list):
                # Handle lists of dicts
                sorted_dict[key] = [sort_dict_keys(item, depth + 1) if isinstance(item, dict) else item for item in value]
            else:
                sorted_dict[key] = value

        return sorted_dict

    # Sort the entire structure
    sorted_data = sort_dict_keys(data)

    # Save sorted JSON
    output_file = Path(output_path) if output_path else json_path
    log(f"Writing sorted JSON to: {output_file}")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(sorted_data, f, indent=2, ensure_ascii=False)

    # Summary
    log("")
    log("=" * 60)
    log("SORT JSON KEYS SUMMARY:")
    log("=" * 60)
    log(f"Total top-level keys sorted: {len(data)}")
    log(f"Sorting order: Capital letters first, then others")
    log(f"Output file: {output_file}")
    log("=" * 60)
    log("✅ Done")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Sort JSON file by keys with capital letters first"
    )
    parser.add_argument(
        "input_json",
        help="JSON file to sort"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: overwrite input file)"
    )

    args = parser.parse_args()

    return sort_json_keys_capitals_first(args.input_json, args.output)


if __name__ == "__main__":
    exit(main())
