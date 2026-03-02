import json
import argparse
import base64
from collections import defaultdict
from pathlib import Path


def b64(value: str) -> str:
    return base64.urlsafe_b64encode(value.encode("utf-8")).decode("ascii").rstrip("=")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("flat_json")
    parser.add_argument("--duplicates", default="duplicates.txt")
    parser.add_argument("--hashmap", default="hashmap.txt")
    args = parser.parse_args()

    with open(args.flat_json, encoding="utf-8") as f:
        data = json.load(f)

    value_to_keys = defaultdict(list)

    for k, v in data.items():
        value_to_keys[v].append(k)

    duplicates = {v: ks for v, ks in value_to_keys.items() if len(ks) > 1}

    # write duplicates
    with open(args.duplicates, "w", encoding="utf-8") as f:
        for value, keys in duplicates.items():
            f.write(f"VALUE: {value}\n")
            for k in keys:
                f.write(f"  - {k}\n")
            f.write("\n")

    # write hashmap
    with open(args.hashmap, "w", encoding="utf-8") as f:
        for value, keys in duplicates.items():
            hash_key = b64(value)
            f.write(f"{hash_key}: {value}\n")

    print(f"✅ Found {len(duplicates)} duplicated values")


if __name__ == "__main__":
    main()