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
    parser = argparse.ArgumentParser(
        description="Unflatten JSON file(s) - supports single or multiple input-output pairs"
    )
    parser.add_argument(
        "files",
        nargs="+",
        help="Input and output files (input1 output1 [input2 output2 ...])"
    )
    args = parser.parse_args()

    # Check if we have pairs of files
    if len(args.files) % 2 != 0:
        parser.error("Please provide pairs of input and output files (input1 output1 input2 output2 ...)")

    # Process each pair
    total_pairs = len(args.files) // 2
    for i in range(total_pairs):
        input_file = args.files[i * 2]
        output_file = args.files[i * 2 + 1]

        flat_path = Path(input_file)
        out_path = Path(output_file)

        if not flat_path.exists():
            log(f"Error: File not found: {flat_path}")
            continue

        try:
            log(f"Loading flattened file: {flat_path}")
            with open(flat_path, encoding="utf-8") as f:
                flat_data = json.load(f)

            log(f"Unflattening {len(flat_data)} keys")
            nested_data = unflatten(flat_data)

            log(f"Writing nested JSON to: {out_path}")
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(nested_data, f, ensure_ascii=False, indent=2)

            log(f"Done, {len(flat_data)} keys unflattened: {flat_path} -> {out_path}")
        except json.JSONDecodeError:
            log(f"Error: Invalid JSON in {flat_path}")
        except Exception as e:
            log(f"Error processing {flat_path}: {e}")

if __name__ == "__main__":
    main()