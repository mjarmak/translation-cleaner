import json
import argparse
from pathlib import Path


def flatten_dict(d, parent_key="", sep="."):
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key, sep))
        else:
            items[new_key] = v
    return items


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Input JSON file")
    parser.add_argument("output", help="Output flattened JSON")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    flat = flatten_dict(data)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(flat, f, ensure_ascii=False, indent=2)

    print(f"✅ Flattened {len(flat)} keys")


if __name__ == "__main__":
    main()