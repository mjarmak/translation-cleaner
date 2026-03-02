import json
import argparse
import time
from pathlib import Path


def log(msg: str):
    print(f"[i18n-clean] {msg}")


def load_keys_to_delete(txt_path: Path) -> set[str]:
    """
    Reads keys from txt file.
    Supports:
      key.one
      key.two
      key.three: something
      - key.four
    """
    keys = set()

    for line in txt_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()

        if not line:
            continue

        # remove bullet prefix
        if line.startswith("- "):
            line = line[2:].strip()

        # take part before colon if present
        if ":" in line:
            line = line.split(":", 1)[0].strip()

        keys.add(line)

    return keys


def main():
    parser = argparse.ArgumentParser(
        description="Delete translation keys from flattened JSON"
    )
    parser.add_argument("flat_json", help="Flattened JSON file")
    parser.add_argument("delete_txt", help="TXT file containing keys to delete")
    parser.add_argument(
        "--out",
        default="cleaned.flat.json",
        help="Output cleaned JSON file",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without modifying",
    )

    args = parser.parse_args()

    start_total = time.time()

    flat_path = Path(args.flat_json)
    delete_path = Path(args.delete_txt)
    out_path = Path(args.out)

    if not flat_path.exists():
        raise FileNotFoundError(f"Flatten file not found: {flat_path}")

    if not delete_path.exists():
        raise FileNotFoundError(f"Delete list not found: {delete_path}")

    # -------------------------------------------------
    # Load flattened file
    # -------------------------------------------------
    log(f"Loading flattened file: {flat_path}")
    with open(flat_path, encoding="utf-8") as f:
        data = json.load(f)

    original_count = len(data)
    log(f"Loaded {original_count} keys")

    # -------------------------------------------------
    # Load keys to delete
    # -------------------------------------------------
    log(f"Loading delete list: {delete_path}")
    keys_to_delete = load_keys_to_delete(delete_path)
    log(f"Keys requested for deletion: {len(keys_to_delete)}")

    # -------------------------------------------------
    # Compute removals
    # -------------------------------------------------
    existing_to_delete = [k for k in keys_to_delete if k in data]
    missing_keys = [k for k in keys_to_delete if k not in data]

    log(f"Keys found and will be removed: {len(existing_to_delete)}")
    log(f"Keys not present in flat file: {len(missing_keys)}")

    if args.dry_run:
        log("🔎 DRY RUN — no changes will be written")
        for k in existing_to_delete[:20]:
            log(f"   would remove: {k}")
        log("✅ Dry run complete")
        return

    # -------------------------------------------------
    # Delete keys
    # -------------------------------------------------
    for k in existing_to_delete:
        del data[k]

    new_count = len(data)

    # -------------------------------------------------
    # Write output
    # -------------------------------------------------
    log(f"Writing cleaned file to: {out_path}")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    log("📊 Summary")
    log(f"Original keys: {original_count}")
    log(f"Removed keys:  {len(existing_to_delete)}")
    log(f"Remaining:     {new_count}")
    log(f"Missing keys in delete list: {len(missing_keys)}")

    log(f"✅ Done in {time.time() - start_total:.2f}s")


if __name__ == "__main__":
    main()