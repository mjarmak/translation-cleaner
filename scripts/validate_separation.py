import json
from pathlib import Path

# Check file counts
flat_path = Path('en.flat.json')
under_path = Path('en.flat.underscore.json')
upper_path = Path('en.flat.uppercase.json')
filt_path = Path('en.flat.filtered.json')

orig = len(json.load(open(flat_path)))
under = len(json.load(open(under_path)))
upper = len(json.load(open(upper_path)))
filt = len(json.load(open(filt_path)))

# Calculate overlap
under_keys = set(json.load(open(under_path)).keys())
upper_keys = set(json.load(open(upper_path)).keys())
overlap = len(under_keys & upper_keys)

print(f"Original: {orig}")
print(f"Underscore: {under}")
print(f"Uppercase: {upper}")
print(f"Filtered: {filt}")
print(f"Overlap (underscore + uppercase): {overlap}")
print(f"Total (under + upper + filt - overlap): {under + upper + filt - overlap}")
print(f"Validation: {'PASS' if under + upper + filt - overlap == orig else 'FAIL'}")
