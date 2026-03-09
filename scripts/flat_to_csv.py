import json
import csv
import argparse
import time
from pathlib import Path


def log(msg: str):
    print(f"[i18n-json2csv] {msg}")


def main():
    parser = argparse.ArgumentParser(
        description="Convert flattened i18n JSON to CSV"
    )
    parser.add_argument("flat_json", help="Flattened JSON input file")
    parser.add_argument(
        "--out",
        default="translations.csv",
        help="Output CSV file",
    )
    parser.add_argument(
        "--delimiter",
        default=",",
        help="CSV delimiter (default: ,)",
    )
    parser.add_argument(
        "--no-header",
        action="store_true",
        help="Do not write CSV header",
    )
    parser.add_argument(
        "--sort",
        action="store_true",
        help="Sort keys alphabetically",
    )

    args = parser.parse_args()

    start_total = time.time()

    flat_path = Path(args.flat_json)
    out_path = Path(args.out)

    if not flat_path.exists():
        raise FileNotFoundError(f"Flatten file not found: {flat_path}")

    # -------------------------------------------------
    # Load JSON
    # -------------------------------------------------
    log(f"Loading flattened file: {flat_path}")
    start = time.time()

    with open(flat_path, encoding="utf-8") as f:
        data = json.load(f)

    log(f"Loaded {len(data)} entries in {time.time() - start:.2f}s")

    # -------------------------------------------------
    # Prepare rows
    # -------------------------------------------------
    log("Preparing CSV rows")

    items = list(data.items())

    if args.sort:
        log("Sorting keys alphabetically")
        items.sort(key=lambda x: x[0])

    # -------------------------------------------------
    # Write CSV
    # -------------------------------------------------
    log(f"Writing CSV to: {out_path}")

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(
            f,
            delimiter=args.delimiter,
            quoting=csv.QUOTE_MINIMAL,
        )

        if not args.no_header:
            writer.writerow(["key", "value"])

        written = 0
        for key, value in items:
            writer.writerow([key, value])
            written += 1

    log(f"Wrote {written} rows")
    log(f"✅ Done in {time.time() - start_total:.2f}s")


if __name__ == "__main__":
    main()