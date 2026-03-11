import json
import argparse
import re
from pathlib import Path
from collections import defaultdict


def log(msg: str):
    print(f"[i18n-unused] {msg}")


def main():
    parser = argparse.ArgumentParser(
        description="Find unused translation keys in project and create a list"
    )
    parser.add_argument(
        "flat_json",
        help="Flattened JSON file containing all translation keys"
    )
    parser.add_argument(
        "src_dir",
        help="Source directory to search for key usage"
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Output directory for unused keys files"
    )

    args = parser.parse_args()

    flat_path = Path(args.flat_json)
    src_path = Path(args.src_dir)
    output_dir = Path(args.out)

    if not flat_path.exists():
        parser.error(f"Flat JSON file not found: {flat_path}")

    if not src_path.exists():
        parser.error(f"Source directory not found: {src_path}")

    # Create output directory if needed
    output_dir.mkdir(parents=True, exist_ok=True)

    log(f"Loading flat JSON: {flat_path}")
    with open(flat_path, encoding="utf-8") as f:
        flat_data = json.load(f)

    log(f"Loaded {len(flat_data)} keys from flat JSON")

    # Find all TypeScript/JavaScript, HTML, and JSON files
    ts_extensions = {".ts", ".js", ".tsx", ".jsx"}
    html_extensions = {".html", ".htm"}
    json_extensions = {".json"}
    feature_extensions = {".feature"}
    all_extensions = ts_extensions | html_extensions | json_extensions | feature_extensions
    project_files = []

    for project_file in src_path.rglob("*"):
        if project_file.is_file() and project_file.suffix in all_extensions:
            project_files.append(project_file)

    log(f"Found {len(project_files)} TypeScript/JavaScript/HTML/JSON files to search")

    # Read all project files and track which keys are used
    used_keys = set()
    file_contents = {}

    for project_file in project_files:
        try:
            with open(project_file, encoding="utf-8") as f:
                content = f.read()
                file_contents[project_file] = content
        except Exception as e:
            log(f"⚠️  Warning: Could not read {project_file}: {e}")

    log(f"Read {len(file_contents)} project files")

    # Check each key for usage
    log("\nSearching for key usage in project files...")

    for key in flat_data.keys():
        # Sort by length (longest first) to avoid partial matches
        # Create patterns for different contexts:
        # 1. 'key' or "key" (string literal)
        # 2. key: (object property)
        # 3. [key] (bracket notation)

        patterns = [
            f"['\"]({re.escape(key)})['\"]",  # 'key' or "key"
            f"\\b{re.escape(key)}\\b",  # as identifier/word
        ]

        key_found = False
        for pattern in patterns:
            try:
                for file_path, content in file_contents.items():
                    if re.search(pattern, content):
                        used_keys.add(key)
                        key_found = True
                        break
                if key_found:
                    break
            except Exception as e:
                log(f"⚠️  Warning: Error searching for key '{key}': {e}")

    # Find unused keys
    unused_keys = sorted([k for k in flat_data.keys() if k not in used_keys])

    log(f"\nKey usage summary:")
    log(f"Total keys: {len(flat_data)}")
    log(f"Used keys: {len(used_keys)}")
    log(f"Unused keys: {len(unused_keys)}")

    # Write combined comprehensive report
    combined_report_path = output_dir / "unused_keys.txt"
    log(f"\nWriting combined report to: {combined_report_path}")

    with open(combined_report_path, "w", encoding="utf-8") as f:
        # Write summary header
        f.write("=" * 60 + "\n")
        f.write("UNUSED KEYS REPORT\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Total keys in flat JSON: {len(flat_data)}\n")
        f.write(f"Used keys: {len(used_keys)}\n")
        f.write(f"Unused keys: {len(unused_keys)}\n")
        f.write(f"Usage percentage: {len(used_keys) / len(flat_data) * 100:.1f}%\n")
        f.write("\n")
        f.write("=" * 60 + "\n")
        f.write(f"UNUSED KEYS LIST ({len(unused_keys)} total):\n")
        f.write("=" * 60 + "\n\n")

        # Write detailed list with values
        for key in unused_keys:
            value = flat_data[key]
            f.write(f"{key}\n")
            f.write(f"  Value: {value}\n\n")

    # Write simple list file (just keys, one per line)
    simple_list_path = output_dir / "unused_keys_list.txt"
    log(f"Writing simple list to: {simple_list_path}")

    with open(simple_list_path, "w", encoding="utf-8") as f:
        for key in unused_keys:
            f.write(f"{key}\n")

    log("")
    log("=" * 60)
    log("UNUSED KEYS DETECTION COMPLETE:")
    log("=" * 60)
    log(f"Combined report: {combined_report_path}")
    log(f"Simple list: {simple_list_path}")
    log(f"Total unused: {len(unused_keys)} out of {len(flat_data)} keys")
    log("=" * 60)
    log("✅ Done")

    return 0


if __name__ == "__main__":
    exit(main())
