import argparse
import re
from pathlib import Path


def log(msg: str):
    print(f"[i18n-filter] {msg}")


def is_all_uppercase(value: str) -> bool:
    """Check if value contains only uppercase letters (and non-letter characters)."""
    # Remove non-alphabetic characters and check if remaining string is uppercase
    letters_only = ''.join(c for c in value if c.isalpha())
    if not letters_only:  # No letters at all
        return False
    return letters_only == letters_only.upper()


def parse_duplicates_file(duplicates_path: Path) -> list[tuple[str, list[tuple[str, str]]]]:
    """
    Parse duplicates file and return list of (value, [(key, value), ...]) tuples.
    Skips the summary header section.
    """
    entries = []
    current_value = None
    current_keys = []

    with open(duplicates_path, encoding="utf-8") as f:
        lines = f.readlines()

    # Skip header section (find the first "VALUE:" line)
    skip_header = True
    for line in lines:
        line = line.rstrip()

        # Skip header
        if skip_header and line.startswith("="):
            continue
        if skip_header and line.startswith("DUPLICATES REPORT"):
            continue
        if skip_header and line.startswith("Total"):
            continue
        if skip_header and line.startswith("Unique"):
            continue
        if skip_header and not line.startswith("VALUE:"):
            continue

        skip_header = False

        if line.startswith("VALUE:"):
            # Save previous entry if exists
            if current_value is not None and current_keys:
                entries.append((current_value, current_keys))

            # Start new entry
            current_value = line.replace("VALUE:", "").strip()
            current_keys = []

        elif line.startswith("  - "):
            # Parse key = value
            match = re.match(r"  - (.+?)\s*=\s*(.+)", line)
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                current_keys.append((key, value))

    # Don't forget the last entry
    if current_value is not None and current_keys:
        entries.append((current_value, current_keys))

    return entries


def write_filtered_report(output_path: Path, entries: list[tuple[str, list[tuple[str, str]]]], title: str):
    """Write filtered duplicates to a file."""
    with open(output_path, "w", encoding="utf-8") as f:
        # Write header
        f.write("=" * 60 + "\n")
        f.write(f"{title}\n")
        f.write("=" * 60 + "\n")
        f.write(f"Total duplicate values found: {len(entries)}\n")

        total_keys = sum(len(keys) for _, keys in entries)
        f.write(f"Total duplicate keys found: {total_keys}\n")
        f.write("=" * 60 + "\n\n")

        # Write entries
        for value, keys in entries:
            f.write(f"VALUE: {value}\n")
            for key, val in keys:
                f.write(f"  - {key} = {val}\n")
            f.write("\n")


def write_canonical_mapping(output_path: Path, entries: list[tuple[str, list[tuple[str, str]]]], prefix: str = ""):
    """Write canonical mapping file (key: canonical_key format)."""
    with open(output_path, "w", encoding="utf-8") as f:
        for value, keys in entries:
            if not keys:
                continue
            # Use first key as the canonical key
            canonical_key = keys[0][0]
            # Write mapping for all other keys to the canonical one
            for key, _ in keys[1:]:
                f.write(f"{key}: {canonical_key}\n")
            # Also add the canonical key itself (maps to itself)
            f.write(f"{canonical_key}: {canonical_key}\n")


def parse_canonical_mapping(mapping_path: Path) -> dict[str, str]:
    """Parse canonical mapping file (key: canonical_key format)."""
    mapping = {}
    if not mapping_path.exists():
        return mapping

    with open(mapping_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or ":" not in line:
                continue
            key, canonical_key = line.split(":", 1)
            mapping[key.strip()] = canonical_key.strip()

    return mapping


def main():
    parser = argparse.ArgumentParser(
        description="Filter duplicates report and canonical mapping into 6 files"
    )
    parser.add_argument("duplicates_report", help="Input duplicates report file")
    parser.add_argument(
        "--canonical-in",
        default="",
        help="Input canonical mapping file to filter",
    )
    parser.add_argument(
        "--underscore-duplicates-out",
        default="duplicates_with_underscore.txt",
        help="Output duplicates report for keys containing underscore",
    )
    parser.add_argument(
        "--underscore-canonical-out",
        default="canonical-mapping_with_underscore.txt",
        help="Output canonical mapping for keys containing underscore",
    )
    parser.add_argument(
        "--uppercase-duplicates-out",
        default="duplicates_all_uppercase.txt",
        help="Output duplicates report for all-uppercase values",
    )
    parser.add_argument(
        "--uppercase-canonical-out",
        default="canonical-mapping_with_uppercase.txt",
        help="Output canonical mapping for all-uppercase values",
    )
    parser.add_argument(
        "--filtered-duplicates-out",
        default="duplicates-filtered.txt",
        help="Output duplicates report without underscore and uppercase items",
    )
    parser.add_argument(
        "--filtered-canonical-out",
        default="canonical-mapping-filtered.txt",
        help="Output canonical mapping without underscore and uppercase items",
    )

    args = parser.parse_args()

    duplicates_path = Path(args.duplicates_report)
    canonical_in_path = Path(args.canonical_in) if args.canonical_in else None
    underscore_dup_out = Path(args.underscore_duplicates_out)
    underscore_can_out = Path(args.underscore_canonical_out)
    uppercase_dup_out = Path(args.uppercase_duplicates_out)
    uppercase_can_out = Path(args.uppercase_canonical_out)
    filtered_dup_out = Path(args.filtered_duplicates_out)
    filtered_can_out = Path(args.filtered_canonical_out)

    if not duplicates_path.exists():
        parser.error(f"Duplicates report not found: {duplicates_path}")

    log(f"Parsing duplicates report: {duplicates_path}")
    entries = parse_duplicates_file(duplicates_path)
    log(f"Loaded {len(entries)} duplicate value groups")

    # Load canonical mapping if provided
    canonical_mapping = {}
    if canonical_in_path and canonical_in_path.exists():
        log(f"Parsing canonical mapping: {canonical_in_path}")
        canonical_mapping = parse_canonical_mapping(canonical_in_path)
        log(f"Loaded {len(canonical_mapping)} canonical mappings")

    # Filter entries with keys containing underscore
    underscore_entries = []
    underscore_keys_set = set()
    for value, keys in entries:
        # Keep only keys that contain '_'
        filtered_keys = [(k, v) for k, v in keys if '_' in k]
        if filtered_keys:
            underscore_entries.append((value, filtered_keys))
            for k, _ in filtered_keys:
                underscore_keys_set.add(k)

    # Filter entries with all-uppercase values
    uppercase_entries = []
    uppercase_keys_set = set()
    for value, keys in entries:
        if is_all_uppercase(value):
            uppercase_entries.append((value, keys))
            for k, _ in keys:
                uppercase_keys_set.add(k)

    # Filter entries without underscore and uppercase
    filtered_entries = []
    for value, keys in entries:
        filtered_keys = [(k, v) for k, v in keys if k not in underscore_keys_set and k not in uppercase_keys_set]
        if filtered_keys:
            filtered_entries.append((value, filtered_keys))

    # Write duplicates reports
    log(f"Writing underscore duplicates to: {underscore_dup_out}")
    write_filtered_report(underscore_dup_out, underscore_entries, "DUPLICATES WITH UNDERSCORE IN KEYS")

    log(f"Writing uppercase duplicates to: {uppercase_dup_out}")
    write_filtered_report(uppercase_dup_out, uppercase_entries, "DUPLICATES WITH ALL-UPPERCASE VALUES")

    log(f"Writing filtered duplicates to: {filtered_dup_out}")
    write_filtered_report(filtered_dup_out, filtered_entries, "DUPLICATES (FILTERED - NO UNDERSCORE/UPPERCASE)")

    # Write canonical mappings
    if canonical_mapping:
        # Underscore canonical mapping
        underscore_canonical = {}
        for key, canonical_key in canonical_mapping.items():
            if key in underscore_keys_set:
                underscore_canonical[key] = canonical_key

        log(f"Writing underscore canonical mapping to: {underscore_can_out}")
        with open(underscore_can_out, "w", encoding="utf-8") as f:
            for key, canonical_key in sorted(underscore_canonical.items()):
                f.write(f"{key}: {canonical_key}\n")
        log(f"Wrote {len(underscore_canonical)} underscore mappings")

        # Uppercase canonical mapping
        uppercase_canonical = {}
        for key, canonical_key in canonical_mapping.items():
            if key in uppercase_keys_set:
                uppercase_canonical[key] = canonical_key

        log(f"Writing uppercase canonical mapping to: {uppercase_can_out}")
        with open(uppercase_can_out, "w", encoding="utf-8") as f:
            for key, canonical_key in sorted(uppercase_canonical.items()):
                f.write(f"{key}: {canonical_key}\n")
        log(f"Wrote {len(uppercase_canonical)} uppercase mappings")

        # Filtered canonical mapping (excluding underscore and uppercase keys)
        filtered_canonical = {}
        for key, canonical_key in canonical_mapping.items():
            if key not in underscore_keys_set and key not in uppercase_keys_set:
                filtered_canonical[key] = canonical_key

        log(f"Writing filtered canonical mapping to: {filtered_can_out}")
        with open(filtered_can_out, "w", encoding="utf-8") as f:
            for key, canonical_key in sorted(filtered_canonical.items()):
                f.write(f"{key}: {canonical_key}\n")
        log(f"Wrote {len(filtered_canonical)} filtered mappings")
    else:
        log("No canonical mapping provided, skipping canonical mapping outputs")

    # Summary
    total_underscore_keys = sum(len(keys) for _, keys in underscore_entries)
    total_uppercase_keys = sum(len(keys) for _, keys in uppercase_entries)
    total_filtered_keys = sum(len(keys) for _, keys in filtered_entries)

    log("")
    log("=" * 60)
    log("FILTER SUMMARY:")
    log("=" * 60)
    log(f"Underscore keys: {total_underscore_keys} keys in {len(underscore_entries)} groups")
    log(f"Uppercase values: {total_uppercase_keys} keys in {len(uppercase_entries)} groups")
    log(f"Filtered (safe): {total_filtered_keys} keys in {len(filtered_entries)} groups")
    log(f"Total excluded: {len(underscore_keys_set | uppercase_keys_set)} keys")
    log("=" * 60)
    log("✅ Done - Generated 6 output files")


if __name__ == "__main__":
    main()
