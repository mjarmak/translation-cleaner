import json
import argparse
import re
from pathlib import Path


def load_hashmap(path: Path):
    mapping = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if ":" in line:
            h, v = line.split(":", 1)
            mapping[v.strip()] = h.strip()
    return mapping


def replace_in_file(path: Path, key_map):
    text = path.read_text(encoding="utf-8", errors="ignore")
    original = text

    for old_key, new_key in key_map.items():
        text = re.sub(
            rf"(['\"])({re.escape(old_key)})(['\"])",
            rf"\1{new_key}\3",
            text,
        )

    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("flat_json")
    parser.add_argument("hashmap_txt")
    parser.add_argument("--src", default="src")
    parser.add_argument("--out", default="flattened.renamed.json")
    args = parser.parse_args()

    with open(args.flat_json, encoding="utf-8") as f:
        flat = json.load(f)

    value_to_hash = load_hashmap(Path(args.hashmap_txt))

    # build key map
    key_map = {}
    for key, value in flat.items():
        if value in value_to_hash:
            key_map[key] = value_to_hash[value]

    # rename flattened
    renamed = {}
    for k, v in flat.items():
        renamed[key_map.get(k, k)] = v

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(renamed, f, ensure_ascii=False, indent=2)

    # rename in project
    changed_files = 0
    for file in Path(args.src).rglob("*"):
        if file.suffix in {".ts", ".html"}:
            if replace_in_file(file, key_map):
                changed_files += 1

    print(f"✅ Renamed {len(key_map)} keys")
    print(f"✅ Updated {changed_files} files")


if __name__ == "__main__":
    main()