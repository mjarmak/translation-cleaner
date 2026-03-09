import json
import argparse


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
    parser = argparse.ArgumentParser(
        description="Flatten JSON file(s) - supports single or multiple input-output pairs"
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

        try:
            with open(input_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            flat = flatten_dict(data)

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(flat, f, ensure_ascii=False, indent=2)

            print(f"Flattened {input_file} -> {output_file} ({len(flat)} keys)")
        except FileNotFoundError:
            print(f"Error: File not found: {input_file}")
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in {input_file}")
        except Exception as e:
            print(f"Error processing {input_file}: {e}")


if __name__ == "__main__":
    main()