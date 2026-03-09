import json
import argparse
from pathlib import Path
from typing import Any, Tuple


def log(msg: str):
    print(f"[i18n-validate] {msg}")


def normalize_value(val: Any) -> Any:
    """Convert all values to comparable format (strings to strings, etc)."""
    if isinstance(val, str):
        return val.strip()
    elif isinstance(val, dict):
        return {k: normalize_value(v) for k, v in val.items()}
    elif isinstance(val, list):
        return [normalize_value(v) for v in val]
    else:
        return val


def deep_compare(original: Any, reconstructed: Any, path: str = "") -> Tuple[bool, list]:
    """
    Recursively compare two JSON structures.
    Returns (is_equal, list_of_differences)
    """
    differences = []

    if type(original) != type(reconstructed):
        differences.append(f"Type mismatch at {path}: {type(original).__name__} vs {type(reconstructed).__name__}")
        return False, differences

    if isinstance(original, dict):
        # Check for missing or extra keys
        orig_keys = set(original.keys())
        recon_keys = set(reconstructed.keys())

        if orig_keys != recon_keys:
            missing = orig_keys - recon_keys
            extra = recon_keys - orig_keys
            if missing:
                for key in sorted(missing):
                    key_path = f"{path}.{key}" if path else key
                    value = original[key]
                    differences.append(f"Missing key: {key_path} = {json.dumps(value)}")
            if extra:
                for key in sorted(extra):
                    key_path = f"{path}.{key}" if path else key
                    value = reconstructed[key]
                    differences.append(f"Extra key: {key_path} = {json.dumps(value)}")
            return False, differences

        # Recursively compare values
        for key in orig_keys:
            new_path = f"{path}.{key}" if path else key
            equal, diffs = deep_compare(original[key], reconstructed[key], new_path)
            if not equal:
                differences.extend(diffs)

    elif isinstance(original, list):
        if len(original) != len(reconstructed):
            differences.append(f"List length mismatch at {path}: {len(original)} vs {len(reconstructed)}")
            return False, differences

        for i, (orig_item, recon_item) in enumerate(zip(original, reconstructed)):
            new_path = f"{path}[{i}]"
            equal, diffs = deep_compare(orig_item, recon_item, new_path)
            if not equal:
                differences.extend(diffs)

    else:
        # Compare primitive values
        orig_norm = normalize_value(original)
        recon_norm = normalize_value(reconstructed)

        if orig_norm != recon_norm:
            differences.append(f"Value mismatch at {path}: '{original}' vs '{reconstructed}'")
            return False, differences

    return len(differences) == 0, differences


def main():
    parser = argparse.ArgumentParser(
        description="Validate that flattening and unflattening preserves the original JSON structure"
    )
    parser.add_argument(
        "files",
        nargs="+",
        help="Original JSON and unflattened JSON file pairs (original1 unflattened1 [original2 unflattened2 ...])"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed comparison output"
    )
    args = parser.parse_args()

    # Check if we have pairs of files
    if len(args.files) % 2 != 0:
        parser.error("Please provide pairs of original and unflattened JSON files (original1 unflattened1 original2 unflattened2 ...)")

    # Process each pair
    total_pairs = len(args.files) // 2
    all_valid = True

    for i in range(total_pairs):
        original_file = args.files[i * 2]
        unflattened_file = args.files[i * 2 + 1]

        orig_path = Path(original_file)
        unflat_path = Path(unflattened_file)

        # Check if files exist
        if not orig_path.exists():
            log(f"Error: Original file not found: {orig_path}")
            all_valid = False
            continue

        if not unflat_path.exists():
            log(f"Error: Unflattened file not found: {unflat_path}")
            all_valid = False
            continue

        try:
            # Load both files
            with open(orig_path, "r", encoding="utf-8") as f:
                original_data = json.load(f)

            with open(unflat_path, "r", encoding="utf-8") as f:
                unflattened_data = json.load(f)

            # Compare structures
            is_equal, differences = deep_compare(original_data, unflattened_data)

            if is_equal:
                log(f"[PASS] {orig_path}")
            else:
                log(f"[FAIL] {orig_path}")
                all_valid = False

                # Show missing/extra keys and their values
                for diff in differences:
                    if "Missing key:" in diff or "Extra key:" in diff:
                        log(f"  {diff}")

                # Show value mismatches only in verbose mode
                if args.verbose:
                    for diff in differences:
                        if "Value mismatch" in diff or "Type mismatch" in diff or "List length" in diff:
                            log(f"  {diff}")
                else:
                    value_mismatch_count = sum(1 for d in differences if "Value mismatch" in d or "Type mismatch" in d or "List length" in d)
                    if value_mismatch_count > 0:
                        log(f"  {value_mismatch_count} value mismatch(es) (use --verbose for details)")

        except json.JSONDecodeError as e:
            log(f"Error: Invalid JSON in {orig_path if "original" in str(e) else unflat_path}: {e}")
            all_valid = False
        except Exception as e:
            log(f"Error processing files: {e}")
            all_valid = False

    # Final summary
    if all_valid:
        log(f"✓ All {total_pairs} validation(s) passed")
        return 0
    else:
        log(f"✗ Some validation(s) failed")
        return 1


if __name__ == "__main__":
    exit(main())
