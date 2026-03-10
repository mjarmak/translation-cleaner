import json
import argparse
import re
from pathlib import Path


def log(msg: str):
    print(f"[i18n-project] {msg}")


def main():
    parser = argparse.ArgumentParser(
        description="Apply canonical mapping to TypeScript/JavaScript project files"
    )
    parser.add_argument(
        "src_dir",
        help="Source directory containing TypeScript/JavaScript files"
    )
    parser.add_argument(
        "mapping_json",
        help="Canonical mapping JSON file from canonical_map.py"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying files"
    )

    args = parser.parse_args()

    src_path = Path(args.src_dir)
    mapping_path = Path(args.mapping_json)
    dry_run = args.dry_run

    if not src_path.exists():
        parser.error(f"Source directory not found: {src_path}")

    if not mapping_path.exists():
        parser.error(f"Mapping JSON file not found: {mapping_path}")

    log(f"Loading mapping JSON: {mapping_path}")
    with open(mapping_path, encoding="utf-8") as f:
        mapping_array = json.load(f)

    log(f"Loaded {len(mapping_array)} mapping entries")

    # Build mapping dictionary: old_key -> new_key
    key_mapping = {}

    for entry in mapping_array:
        for key_entry in entry["keys"]:
            old_key = key_entry["key"]
            map_key_to = entry["mapKeyTo"]
            key_mapping[old_key] = map_key_to

    log(f"Built mapping for {len(key_mapping)} keys")

    # Find all TypeScript/JavaScript and HTML files
    ts_extensions = {".ts", ".js", ".tsx", ".jsx"}
    html_extensions = {".html", ".htm"}
    all_extensions = ts_extensions | html_extensions
    project_files = []

    for project_file in src_path.rglob("*"):
        if project_file.is_file() and project_file.suffix in all_extensions:
            project_files.append(project_file)

    log(f"Found {len(project_files)} TypeScript/JavaScript/HTML files")

    # Apply mapping to each file
    total_replacements = 0
    files_modified = 0

    for project_file in project_files:
        try:
            with open(project_file, encoding="utf-8") as f:
                content = f.read()

            original_content = content
            replacements_in_file = 0

            # Sort keys by length (longest first) to avoid partial replacements
            sorted_keys = sorted(key_mapping.keys(), key=len, reverse=True)

            for old_key in sorted_keys:
                new_key = key_mapping[old_key]

                # Match the key in various contexts:
                # 1. 'old_key' or "old_key"
                # 2. old_key: (in object literals)
                # 3. i18n.old_key or similar patterns

                # Create pattern that matches the key as a string literal or identifier
                patterns = [
                    (f"['\"]({re.escape(old_key)})['\"]", f"'{new_key}'"),  # 'key' or "key"
                    (f"(?<!['\"])\\b{re.escape(old_key)}\\b(?!['\"])", new_key),  # identifier
                ]

                for pattern, replacement in patterns:
                    matches = re.finditer(pattern, content)
                    match_count = len(list(re.finditer(pattern, content)))

                    if match_count > 0:
                        content = re.sub(pattern, replacement, content)
                        replacements_in_file += match_count

            if content != original_content:
                files_modified += 1
                total_replacements += replacements_in_file

                if not dry_run:
                    with open(project_file, "w", encoding="utf-8") as f:
                        f.write(content)
                    log(f"✓ {project_file.relative_to(src_path)}: {replacements_in_file} replacements")
                else:
                    log(f"[DRY RUN] {project_file.relative_to(src_path)}: {replacements_in_file} replacements")

        except Exception as e:
            log(f"✗ Error processing {project_file}: {e}")

    # Summary
    log("")
    log("=" * 60)
    log("PROJECT MAPPING SUMMARY:")
    log("=" * 60)
    log(f"Files processed: {len(project_files)}")
    log(f"Files modified: {files_modified}")
    log(f"Total replacements: {total_replacements}")
    if dry_run:
        log("Mode: DRY RUN (no files were modified)")
    else:
        log("Mode: ACTUAL (files were modified)")
    log("=" * 60)
    log("✅ Done")

    return 0


if __name__ == "__main__":
    exit(main())
