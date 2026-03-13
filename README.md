# Translation Cleaner

## File Variables

``` bash
INPUT_FILE = ./files/en.json
FLAT_JSON = ./output/flat/en.flat.json
FLAT_JSON_FR = ./output/flat/fr.flat.json
FLAT_JSON_NL = ./output/flat/nl.flat.json
FLAT_JSON_DE = ./output/flat/de.flat.json
USAGE_REPORT = ./output/usage.report.csv
USAGE_REPORT_IGNORE_CASE = ./output/usage-ignore-case.report.csv
DUPLICATES_REPORT = ./output/en_duplicates.report.txt
CANONICAL_MAPPING = ./output/en_canonical-mapping.txt
CANONICAL_MAPPING_JSON = ./output/en_canonical-mapping.json
HASH_RENAME_MAPPING = ./output/hash_rename-mapping.txt
REMOVE_LIST = ./files/remove.txt
FLAT_JSON_CLEAN = ./output/flat/en.flat.clean.json
UNFLAT_JSON = ./output/unflat/en.unflat.json
FLAT_CSV = ./output/flat/en.flat.csv
PROJECT_SRC = C:/Users/mjarmaka/Code/projects/gitlab/nctsp5-ui-dev/src
```

## 1.1. flatten:

Flatten all language files at once:
`python ./scripts/flatten_json.py ./files/en.json ./output/flat/en.flat.json ./files/fr.json ./output/flat/fr.flat.json ./files/nl.json ./output/flat/nl.flat.json ./files/de.json ./output/flat/de.flat.json`

## 1.2 . separate keys that contain '_' and all uppercase values
**Files:** `FLAT_JSON` → `FLAT_JSON_UNDERSCORE` + `FLAT_JSON_UPPERCASE` + `FLAT_JSON_FILTERED`

Use the outputs to manually prepare keys in the projects for hashing replacement in the next steps:

-  Underscore files (`*.underscore.json`) contain keys with `_` or uppercase word segments (e.g., `CANCELLED`, `DOCUMENTARY`, `LAST_12_MONTHS`)
-  Uppercase files (`*.uppercase.json`) contain all-uppercase VALUES
-  Filtered files (`*.filtered.json`) contain safe keys with normal case for processing

**Separate all languages using English as the reference for categories (generates all 3 files for each language):**

`python ./scripts/separate_flat_uppercase_keys.py ./output/flat/en.flat.json --output-dir ./output/flat_separated --language-files "./output/flat/fr.flat.json,./output/flat/nl.flat.json,./output/flat/de.flat.json"`

**Output files generated in the specified output directory (all 3 files for each language):**
- `en.flat.underscore.json`, `en.flat.uppercase.json`, `en.flat.filtered.json`
- `fr.flat.underscore.json`, `fr.flat.uppercase.json`, `fr.flat.filtered.json`
- `nl.flat.underscore.json`, `nl.flat.uppercase.json`, `nl.flat.filtered.json`
- `de.flat.underscore.json`, `de.flat.uppercase.json`, `de.flat.filtered.json`

## 1.3. manual processing of underscore and uppercase keys in the project:

- For the underscore keys, manually review the `*.underscore.json` files to check if they are used in the project, and update the keys manually.
- For the uppercase keys, manually add an uppercase css class to the corresponding elements in the project, so that the values can be safely renamed to a hash without losing the uppercase formatting.
- Then copy all manually processed files to [result](output%2Fresult) for safe keeping.

## 2. usage report (in project):
**Files:** `FLAT_JSON` → `USAGE_REPORT` or `USAGE_REPORT_IGNORE_CASE`

Case checking is for translation keys. So best not to ignore case.

#### case sensitive with language values:
`python ./scripts/usage_report.py ./output/flat/en.flat.json --src C:/Users/mjarmaka/Code/projects/gitlab/nctsp5-ui-dev/src --out ./output/usage.report.csv --languages "./output/flat/fr.flat.json,./output/flat/nl.flat.json,./output/flat/de.flat.json"`,

## 3.1. create mapping of duplicate keys to their canonical key:
**Files:** `FLAT_JSON` → `DUPLICATES.JSON`

Only en is needed to create the mapping. The output is a JSON file with duplicate values and their corresponding keys.

**JSON Structure:**
```json
[
  {
    "value": "Container Indicator",
    "count": 4,
    "mapKeyTo": "hash_containerIndicator",
    "mapValueTo": "Container Indicator",
    "keys": [
      {"key": "app.containerIndicator", "value": "Container Indicator"},
      {"key": "des.registerArrivalNotification.containerIndicator", "value": "Container indicator"},
      ...
    ]
  }
]
```

- `value`: The shared translation value (as-is from first occurrence)
- `count`: Number of keys with this value
- `mapKeyTo`: Last word after the final dot (.) in the first key, with optional prefix
- `mapValueTo`: The value in PascalCase (every word starts with uppercase) selected from the duplicate group. If no PascalCase value exists, uses the original value
- `keys`: Array of all keys and their values

**Value Normalization:** Keys are automatically merged if they have the same value after:
1. **Trimming** leading and trailing whitespace
2. **Removing all internal spaces**

For example, these values would be merged into a single group:
- `"Container Indicator"`
- `"Container  Indicator"` (double space)
- `"  Container Indicator  "` (leading/trailing spaces)
- `"Container    Indicator"` (multiple spaces)

This helps identify translation keys that are semantically identical but have different spacing.

**Protected Namespaces:** Keys in the following namespaces are NOT merged/deduplicated:
- `i18n.errors.*`
- `i18n.options.*`
- `i18n.status.*`

These protected keys are included in the output with `count: 1` and `mapKeyTo` set to the original key itself, preventing any remapping.

All other keys (including those in `i18n.common.*` and other `i18n.*` namespaces) will be deduplicated if they have the same normalized value.

#### case insensitive

`python ./scripts/canonical_map.py ./output/flat/en.flat.json --duplicates-out ./output/remap/en_mapping.json --prefix i18n.common. --ignore-case`

[//]: # (#### case sensitive)

[//]: # ()
[//]: # (`python ./scripts/canonical_map.py ./output/result/en.flat.filtered.json --duplicates-out ./output/remap/en_duplicates-case-sensitive.json --prefix i18n.common`)

## 3.2. sort mapping by value:
**Files:** `MAPPING_JSON` → Sorted `MAPPING_JSON`

Sorts the mapping JSON file alphabetically by the `value` field (case-insensitive). This is useful for:
- Easy review of all translations
- Identifying similar values
- Better organization for readability

`python ./scripts/sort_mapping_by_value.py ./output/remap/en_mapping.json -o ./output/remap/en_mapping_sorted.json`

## 3.3. reorganize mapping by word count:

**Files:** `MAPPING_JSON` → Reorganized `MAPPING_JSON`

Improves the mapping file by moving keys with values below 6 words to `i18n.common` namespace. This helps organize short, commonly-used translations (like buttons, labels, etc.) into a central location.

**Rules:**
- Keys with values containing less than 6 words are moved to `i18n.common.<last_key_part>`
- Keys already under `i18n` namespace are ignored (not moved)
- Output replaces the input file or can be saved to a new file

`python ./scripts/reorganize_mapping_by_word_count.py ./output/remap/en_mapping_sorted.json -o ./output/remap/en_mapping_reorganized.json`

**sort**

`python ./scripts/sort_mapping_by_value.py ./output/remap/en_mapping_reorganized.json`

**Example transformations:**
- `advanceSearch.labels.containerIndicator` (value: "Container Indicator" - 2 words) → `i18n.common.containerIndicator`
- `form.labels.submit` (value: "Submit" - 1 word) → `i18n.common.submit`
- `helpText.invalidEmail` (value: "Please enter a valid email address" - 6 words, not moved)

## 3.4 validate no duplicate mapKeyTo values and verify key existence

- After creating the duplicates JSON file, validate that there are no duplicate `mapKeyTo` values:

`python ./scripts/validate_duplicates.py ./output/remap/en_mapping_reorganized.json`

- Ensure that the mapping file contains all keys from the flat JSON file AND that all keys in the mapping file actually exist in the flat JSON (no orphaned/invalid keys):

`python ./scripts/validate_mapping_coverage.py ./output/flat/en.flat.json ./output/result/en_mapping_reorganized.json`

The validator checks:
1. ✅ All keys from the flat JSON file are covered in the mapping file
2. ✅ All keys in the mapping file exist in the flat JSON file (no orphaned keys)
3. ✅ No duplicate keys
4. ✅ Bidirectional coverage validation

Use `--verbose` to see detailed lists of any missing or invalid keys:

`python ./scripts/validate_mapping_coverage.py ./output/flat/en.flat.json ./output/result/en_mapping_reorganized.json --verbose`

**Note:** The `canonical_map.py` script automatically resolves duplicate `mapKeyTo` conflicts by appending hash suffixes (e.g., `mapKeyTo_hash123`), so this validation should pass if the script ran correctly.

## 4. rename keys (in project and translation files):
**Files:** `FLAT_JSON` + `DUPLICATES.JSON` → `FLAT_JSON_MAPPED` + Updated Project Files

Applies canonical mapping to rename keys by `mapKeyTo` and optionally rename values by `mapValueTo`.

### Apply on i18n JSON files

For **English**: Use `--mapValues` to replace both keys and values

`python ./scripts/apply_mapping_flat_json.py ./output/flat/en.flat.json ./output/result/en_mapping_reorganized.json --out ./output/mapped/en.flat.mapped.json --mapValues`

For **other languages**: Omit `--mapValues` to replace only keys and keep original language values

`python ./scripts/apply_mapping_flat_json.py ./output/flat/fr.flat.json ./output/result/en_mapping_reorganized.json --out ./output/mapped/fr.flat.mapped.json`

`python ./scripts/apply_mapping_flat_json.py ./output/flat/nl.flat.json ./output/result/en_mapping_reorganized.json --out ./output/mapped/nl.flat.mapped.json`

`python ./scripts/apply_mapping_flat_json.py ./output/flat/de.flat.json ./output/result/en_mapping_reorganized.json --out ./output/mapped/de.flat.mapped.json`

The `apply_mapping_flat_json.py` script does the following in one pass:
1. **Copies** the input file to a new output file
2. **Applies mapping** - renames keys to `mapKeyTo` and optionally values to `mapValueTo`
3. **Removes duplicates** - keeps only the first (mapped) key and removes all other duplicate keys from the same value group

## Apply on project files (TypeScript/JavaScript/HTML/JSON/FEATURE)

Applies mapping to all `.ts`, `.js`, `.tsx`, `.jsx`, `.html`, `.htm`, `.feature` and `.json` files in the project.

### Dry-Run mapping:

`python ./scripts/apply_mapping_project.py C:/Users/mjarmaka/Code/projects/gitlab/nctsp5-ui-dev/src ./output/result/en_mapping_reorganized.json --dry-run`

### Actual mapping:

`python ./scripts/apply_mapping_project.py C:/Users/mjarmaka/Code/projects/gitlab/nctsp5-ui-dev/src ./output/result/en_mapping_reorganized.json`

### Mapping on tests:

#### Playwright
`python ./scripts/apply_mapping_project.py C:/Users/mjarmaka/Code/projects/gitlab/nctsp5-ui-dev/tests ./output/result/en_mapping_reorganized.json`

#### Cypress
`python ./scripts/apply_mapping_project.py C:/Users/mjarmaka/Code/projects/gitlab/nctsp5-ui-dev/cypress ./output/result/en_mapping_reorganized.json`

### Mapping on tests with label prefix:

To prepend prefixes to all keys being searched, use the `--prefix` option with comma-separated values:

#### Playwright
`python ./scripts/apply_mapping_project.py C:/Users/mjarmaka/Code/projects/gitlab/nctsp5-ui-dev/tests ./output/result/en_mapping_reorganized.json --prefix label-,input-,mat-select-,textarea-`

#### Cypress
`python ./scripts/apply_mapping_project.py C:/Users/mjarmaka/Code/projects/gitlab/nctsp5-ui-dev/cypress ./output/result/en_mapping_reorganized.json --prefix label-,input-,mat-select-,textarea-`

## 5. find unused translation keys:
**Files:** `MAPPING_JSON` + `PROJECT_SRC` → `UNUSED_MAPPED_KEYS_LIST`

Scans all TypeScript/JavaScript/HTML/JSON/FEATURE files in the project to find which translation keys are NOT used anywhere.

Manually review the list of unused keys before deletion, as some keys may be used dynamically or in ways that static analysis cannot detect.

Creates two output files:
1. `unused_keys.txt` - Simple list of unused keys (one per line) for deletion
2. `unused_keys_summary.txt` - Detailed report with statistics and key values

`python ./scripts/find_unused_keys.py ./output/mapped/en.flat.mapped.json C:/Users/mjarmaka/Code/projects/gitlab/nctsp5-ui-dev/src --out ./output/remove_unused`

## 6. delete unused keys:
**Files:** `FLAT_JSON` + `MAPPING_JSON` + `UNUSED_MAPPED_KEYS_LIST` → `FLAT_JSON_CLEAN`

Removes all unused keys from the flat JSON files based on the unused mapped keys list. Uses the mapping file to find all original sub-keys that correspond to unused mapped keys, then deletes them.

**The script:**
1. **Reads** the mapping JSON file to get the relationship between mapKeyTo and sub-keys
2. **Loads** the unused mapped keys list (output from `find_unused_keys.py`)
3. **Finds** all sub-keys that map to the unused mapped keys
4. **Removes** ALL those sub-keys from the flat JSON files

### Preview changes (dry-run)

`python ./scripts/delete_unused_keys.py ./output/mapped/en.flat.mapped.json ./output/remove_unused/unused_keys_list.txt --out ./output/remove_unused/en.flat.clean.json --dry-run`

### Apply actual deletion

`python ./scripts/delete_unused_keys.py ./output/mapped/en.flat.mapped.json ./output/remove_unused/unused_keys_list.txt --out ./output/remove_unused/en.flat.clean.json`

`python ./scripts/delete_unused_keys.py ./output/mapped/fr.flat.mapped.json ./output/remove_unused/unused_keys_list.txt --out ./output/remove_unused/fr.flat.clean.json`

`python ./scripts/delete_unused_keys.py ./output/mapped/nl.flat.mapped.json ./output/remove_unused/unused_keys_list.txt --out ./output/remove_unused/nl.flat.clean.json`

`python ./scripts/delete_unused_keys.py ./output/mapped/de.flat.mapped.json ./output/remove_unused/unused_keys_list.txt --out ./output/remove_unused/de.flat.clean.json`

## 7. copy underscore keys back to filtered files:

Copy the content of the underscore files back to the filtered files before unflattening, so that the unflattened files contain all keys (including those with underscores and uppercase segments).

Copy the keys in [result](output%2Fresult).

Uppercase keys should have been copied back after the manual CSS updates in 1.3.

## 8. unflatten:
**Files:** `FLAT_JSON` + `FLAT_JSON_FR` + `FLAT_JSON_NL` + `FLAT_JSON_DE` → All unflattened outputs

- Unflatten all language files at once:

`python ./scripts/unflatten_json.py
./output/mapped/en.flat.mapped.json ./output/unflat/en.json
./output/mapped/fr.flat.mapped.json ./output/unflat/fr.json
./output/mapped/nl.flat.mapped.json ./output/unflat/nl.json
./output/mapped/de.flat.mapped.json ./output/unflat/de.json
`

Or unflatten them individually:

`python ./scripts/unflatten_json.py ./output/mapped/en.flat.mapped.json ./output/unflat/en.json`

`python ./scripts/unflatten_json.py ./output/mapped/fr.flat.mapped.json ./output/unflat/fr.json`

`python ./scripts/unflatten_json.py ./output/mapped/nl.flat.mapped.json ./output/unflat/nl.json`

`python ./scripts/unflatten_json.py ./output/mapped/de.flat.mapped.json ./output/unflat/de.json`

# Extras:

- ## convert flat to csv:
**Files:** `FLAT_JSON` → `FLAT_CSV`

`python ./scripts/flat_to_csv.py ./output/flat/en.flat.json --out ./output/en.flat.csv`

- ## validate flatten ↔ unflatten:
**Files:** Original JSON + Unflattened → Validation

Validate that the original JSON file is the same as the unflattened file (ensuring no data loss during the flatten/unflatten process):

Validate all language files at once:

`python ./scripts/validate_flatten_unflatten.py ./files/en.json ./output/unflat/en.unflat.json ./files/fr.json ./output/unflat/fr.unflat.json ./files/nl.json ./output/unflat/nl.unflat.json ./files/de.json ./output/unflat/de.unflat.json`

Or validate them individually:

`python ./scripts/validate_flatten_unflatten.py ./files/en.json ./output/unflat/en.unflat.json --verbose`

`python ./scripts/validate_flatten_unflatten.py ./files/fr.json ./output/unflat/fr.unflat.json --verbose`

`python ./scripts/validate_flatten_unflatten.py ./files/nl.json ./output/unflat/nl.unflat.json --verbose`

`python ./scripts/validate_flatten_unflatten.py ./files/de.json ./output/unflat/de.unflat.json --verbose`

- ## Sort JSON by keys with capitals first:
**Files:** `UNFLAT_JSON` → Sorted `UNFLAT_JSON`

Sorts a JSON file by its keys with keys starting with capital letters appearing first, then alphabetically within each group. Useful for organizing translation files for better readability and maintaining consistent structure.

**Sort and overwrite the file:**

`python ./scripts/sort_json_keys_capitals_first.py ./output/unflat/en.json`

**Save to a different file:**

`python ./scripts/sort_json_keys_capitals_first.py ./output/unflat/en.json -o ./output/unflat/en.json.sorted`

**Sort all language files:**

`python ./scripts/sort_json_keys_capitals_first.py ./output/unflat/en.json`

`python ./scripts/sort_json_keys_capitals_first.py ./output/unflat/fr.json`

`python ./scripts/sort_json_keys_capitals_first.py ./output/unflat/nl.json`

`python ./scripts/sort_json_keys_capitals_first.py ./output/unflat/de.json`

**Sorting order:**
1. Keys starting with capital letters (A-Z) - sorted alphabetically (case-insensitive)
2. Keys starting with lowercase letters (a-z) - sorted alphabetically (case-insensitive)
3. Other keys - sorted alphabetically

The script recursively sorts keys in nested objects while preserving the complete JSON structure.

- ## Validate remapped output:
**Files:** `REMAPPED_JSON` + `MAPPING_JSON` → Validation Report

Validates that all keys in a remapped JSON file exist in the mapping file's `mapKeyTo` values. This ensures that the remapping was applied correctly and no orphaned or invalid keys are present in the output.

Supports both JSON object format (nested dictionaries) and JSON array format (lists of objects).

**Ignored Keys:** Keys in the `i18n.*` namespace are automatically ignored during validation (e.g., `i18n`, `i18n.actions`, `i18n.common`, `i18n.discrepancies`, etc.).

The validator checks:
1. ✅ All non-i18n keys in the remapped JSON file exist in the mapping's `mapKeyTo` values
2. ✅ No orphaned keys that were not part of the original mapping
3. ✅ Works with both JSON objects and JSON arrays

**Validate remapped unflat JSON files:**

`python ./scripts/validate_remapped_output.py ./output/unflat/en.json ./output/result/en_mapping_reorganized.json --verbose`

`python ./scripts/validate_remapped_output.py ./output/unflat/fr.json ./output/result/en_mapping_reorganized.json --verbose`

`python ./scripts/validate_remapped_output.py ./output/unflat/nl.json ./output/result/en_mapping_reorganized.json --verbose`

`python ./scripts/validate_remapped_output.py ./output/unflat/de.json ./output/result/en_mapping_reorganized.json --verbose`
