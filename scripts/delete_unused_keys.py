import json
import argparse
from pathlib import Path


def log(msg: str):
    print(f"[i18n-delete] {msg}")


def main():
    parser = argparse.ArgumentParser(
        description="Delete unused translation keys from flat JSON file"
    )
    parser.add_argument(
        "flat_json",
        help="Flattened JSON file to delete keys from"
    )
    parser.add_argument(
        "unused_keys_list",
        help="Text file with list of unused keys (one per line)"
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Output file with unused keys removed"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview deletions without modifying files"
    )

    args = parser.parse_args()

    flat_path = Path(args.flat_json)
    unused_path = Path(args.unused_keys_list)
    output_path = Path(args.out)
    dry_run = args.dry_run

    if not flat_path.exists():
        parser.error(f"Flat JSON file not found: {flat_path}")

    if not unused_path.exists():
        parser.error(f"Unused keys list not found: {unused_path}")

    # Create output directory if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)

    log(f"Loading flat JSON: {flat_path}")
    with open(flat_path, encoding="utf-8") as f:
        flat_data = json.load(f)

    log(f"Loaded {len(flat_data)} keys from flat JSON")

    # Load unused keys list
    log(f"Loading unused keys list: {unused_path}")
    unused_keys = set()
    with open(unused_path, encoding="utf-8") as f:
        for line in f:
            key = line.strip()
            if key:  # Skip empty lines
                unused_keys.add(key)

    log(f"Loaded {len(unused_keys)} unused keys")

    # Create cleaned data by removing unused keys
    cleaned_data = {k: v for k, v in flat_data.items() if k not in unused_keys}

    keys_deleted = len(flat_data) - len(cleaned_data)
    keys_kept = len(cleaned_data)

    # Verify all unused keys were found in the flat JSON
    not_found = unused_keys - set(flat_data.keys())
    if not_found:
        log(f"\n⚠️  Warning: {len(not_found)} keys from unused list not found in flat JSON:")
        for key in sorted(not_found):
            log(f"   - {key}")

    # Write output
    if not dry_run:
        log(f"\nWriting cleaned JSON to: {output_path}")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
    else:
        log(f"\n[DRY RUN] Would write {len(cleaned_data)} keys to: {output_path}")

    # Summary
    log("")
    log("=" * 60)
    log("DELETION SUMMARY:")
    log("=" * 60)
    log(f"Original keys: {len(flat_data)}")
    log(f"Keys to delete: {keys_deleted}")
    log(f"Keys to keep: {keys_kept}")
    log(f"Keys not found in flat JSON: {len(not_found)}")
    if dry_run:
        log("Mode: DRY RUN (no files were modified)")
    else:
        log("Mode: ACTUAL (file was modified)")
    log("=" * 60)
    log("✅ Done")

    return 0


if __name__ == "__main__":
    exit(main())
