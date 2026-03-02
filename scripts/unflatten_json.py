import json
import argparse
from pathlib import Path

def log(msg: str):
    print(f"[i18n-unflatten] {msg}")

def unflatten(flat_dict: dict[str, str]) -> dict:
    """
    Convert flattened dict with dot-separated keys into nested dict.
    """
    nested = {}
    for flat_key, value in flat_dict.items():
        keys = flat_key.split(".")
        d = nested
        for k in keys[:-1]:
            if k not in d or not isinstance(d[k], dict):
                d[k] = {}
            d = d[k]
        d[keys[-1]] = value
    return nested

def main():
    parser = argparse.ArgumentParser(description="Unflatten a flattened i18n JSON file")
    parser.add_argument("flat_json", help="Flattened JSON input file")
    parser.add_argument(
        "--out",
        default="unflattened.json",
        help="Output file for nested JSON",
    )
    args = parser.parse_args()

    flat_path = Path(args.flat_json)
    out_path = Path(args.out)

    if not flat_path.exists():
        raise FileNotFoundError(f"Flattened file not found: {flat_path}")

    log(f"Loading flattened file: {flat_path}")
    with open(flat_path, encoding="utf-8") as f:
        flat_data = json.load(f)

    log(f"Unflattening {len(flat_data)} keys")
    nested_data = unflatten(flat_data)

    log(f"Writing nested JSON to: {out_path}")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(nested_data, f, ensure_ascii=False, indent=2)

    log(f"✅ Done, {len(flat_data)} keys unflattened")

if __name__ == "__main__":
    main()