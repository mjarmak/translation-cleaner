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

## Order of operations:

### 1.1. flatten:

Flatten all language files at once:
`python ./scripts/flatten_json.py ./files/en.json ./output/flat/en.flat.json ./files/fr.json ./output/flat/fr.flat.json ./files/nl.json ./output/flat/nl.flat.json ./files/de.json ./output/flat/de.flat.json`

### 1.2 . separate keys that contain '_' and all uppercase values
**Files:** `FLAT_JSON` → `FLAT_JSON_UNDERSCORE` + `FLAT_JSON_UPPERCASE` + `FLAT_JSON_FILTERED`

Use the outputs to manually prepare keys in the projects for hashing replacement in the next steps:

-  Manually add an 'uppercase' css style to the html of the all uppercase values, then merge the keys in the next steps.
-  Manually review the underscore keys before applying transformations.

**Separate all languages using English as the reference for categories (generates all 3 files for each language):**

`python ./scripts/separate_flat_uppercase_keys.py ./output/flat/en.flat.json --output-dir ./output/flat_separated --language-files "./output/flat/fr.flat.json,./output/flat/nl.flat.json,./output/flat/de.flat.json"`

**Output files generated in the specified output directory (all 3 files for each language):**
- `en.flat.underscore.json`, `en.flat.uppercase.json`, `en.flat.filtered.json`
- `fr.flat.underscore.json`, `fr.flat.uppercase.json`, `fr.flat.filtered.json`
- `nl.flat.underscore.json`, `nl.flat.uppercase.json`, `nl.flat.filtered.json`
- `de.flat.underscore.json`, `de.flat.uppercase.json`, `de.flat.filtered.json`

### 2. usage report (in project):
**Files:** `FLAT_JSON` → `USAGE_REPORT` or `USAGE_REPORT_IGNORE_CASE`

`python ./scripts/usage_report.py ./output/flat/en.flat.json --src C:/Users/mjarmaka/Code/projects/gitlab/nctsp5-ui-dev/src --out ./output/usage.report.csv --languages "./output/flat/fr.flat.json,./output/flat/nl.flat.json,./output/flat/de.flat.json"`,

### 3. create mapping of duplicate keys to their canonical key:
**Files:** `FLAT_JSON` → `CANONICAL_MAPPING` + `DUPLICATES_REPORT`

Only en is needed to create the mapping, then it can be applied to all languages.

The mapping file will contain the canonical key for each duplicate key, and the duplicates report will list all the duplicate keys and their corresponding canonical key.

Case-insensitive finds more duplicates, but it may also create false positives if there are keys that differ only by case but have different meanings.

Case-sensitive will be more strict and only find exact duplicates, but it may miss some duplicates that differ only by case.

A prefix 'hash_' is added to the canonical keys to more easily identify them as the keys that should be renamed to the hashed keys in the project files.

#### case insensitive

`python ./scripts/canonical_map.py ./output/flat/en.flat.json --duplicates-out ./output/hash/en_duplicates.report.txt --mapping-out ./output/hash/en_canonical-mapping.txt --prefix hash_ --ignore-case`

#### case sensitive

`python ./scripts/canonical_map.py ./output/flat/en.flat.json --duplicates-out ./output/hash/en_duplicates-case_sensititve.report.txt --mapping-out ./output/hash/en_canonical-mapping-case_sensititve.txt --prefix hash_`

### 4. rename keys (in project and translation files):
Renames keys in the project and translations, then delete duplicates in the translation files.

#### Apply on i18n json files

`python ./scripts/apply_mapping_flat_json.py ./output/flat/en.flat.json ./output/canonical/en_canonical-mapping.txt --out ./output/replaced/en.flat.mapped.json`

`python ./scripts/apply_mapping_flat_json.py ./output/flat/fr.flat.json ./output/canonical/en_canonical-mapping.txt --out ./output/replaced/fr.flat.mapped.json`

`python ./scripts/apply_mapping_flat_json.py ./output/flat/nl.flat.json ./output/canonical/en_canonical-mapping.txt --out ./output/replaced/nl.flat.mapped.json`

`python ./scripts/apply_mapping_flat_json.py ./output/flat/de.flat.json ./output/canonical/replaced/en_canonical-mapping.txt --out ./output/replaced/de.flat.mapped.json`

#### Apply on project files
`python ./scripts/apply_mapping_project.py C:/Users/mjarmaka/Code/projects/gitlab/nctsp5-ui-dev/src ./output/canonical/en_canonical-mapping.txt`

### 5. rename hashed keys to meaning translation keys (in project and translation files):
**Files:** `CANONICAL_MAPPING_JSON` + `HASH_RENAME_MAPPING` → `FLAT_JSON*`

Run the following scripts to create a mapping file for the hashed keys in the 'common.<key>' format.

The hashed keys are identified by looking at the 'hash_' prefix in the key names.

`python ./scripts/rename_hashed_keys.py ./output/en_canonical-mapping.json ./output/hash_rename-mapping.txt --prefix hash_ --out ./output/hash_rename-mapping.txt`

#### Apply on i18n json files
Then run the rename script below again to update the project and translation files.

`python ./scripts/apply_mapping_flat_json.py ./output/flat/en.flat.json ./output/hash_rename-mapping.txt`

`python ./scripts/apply_mapping_flat_json.py ./output/flat/fr.flat.json ./output/hash_rename-mapping.txt`

`python ./scripts/apply_mapping_flat_json.py ./output/flat/nl.flat.json ./output/hash_rename-mapping.txt`

`python ./scripts/apply_mapping_flat_json.py ./output/flat/de.flat.json ./output/hash_rename-mapping.txt`

#### Apply on project files
`python ./scripts/apply_mapping_project.py C:/Users/mjarmaka/Code/projects/gitlab/nctsp5-ui-dev/src ./output/hash_rename-mapping.txt`

### 6. delete unused keys:
**Files:** `FLAT_JSON` + `REMOVE_LIST` → `FLAT_JSON_CLEAN`

Manually update the output of step 2 (usage report) to create a list of keys to be removed. Save that list in `REMOVE_LIST` and then run the command below.

Keep in mind that some keys are concatenated in the .ts files, such as statuses and options, so you should not those keys.

#### dry run (safe preview of what would be deleted)

`python ./scripts/delete_translations.py ./output/flat/en.flat.json ./files/remove.txt --dry-run`

#### actual deletion

`python ./scripts/delete_translations.py ./output/flat/en.flat.json ./files/remove.txt --out ./output/en.flat.clean.json`

### 7. unflatten:
**Files:** `FLAT_JSON` + `FLAT_JSON_FR` + `FLAT_JSON_NL` + `FLAT_JSON_DE` → All unflattened outputs

Unflatten all language files at once:

`python ./scripts/unflatten_json.py ./output/flat/en.flat.json ./output/unflat/en.unflat.json ./output/flat/fr.flat.json ./output/unflat/fr.unflat.json ./output/flat/nl.flat.json ./output/unflat/nl.unflat.json ./output/flat/de.flat.json ./output/unflat/de.unflat.json`

Or unflatten them individually:

`python ./scripts/unflatten_json.py ./output/flat/en.flat.json ./output/unflat/en.unflat.json`

`python ./scripts/unflatten_json.py ./output/flat/fr.flat.json ./output/unflat/fr.unflat.json`

`python ./scripts/unflatten_json.py ./output/flat/nl.flat.json ./output/unflat/nl.unflat.json`

`python ./scripts/unflatten_json.py ./output/flat/de.flat.json ./output/unflat/de.unflat.json`

### 8. validate flatten ↔ unflatten:
**Files:** Original JSON + Unflattened → Validation

Validate that the original JSON file is the same as the unflattened file (ensuring no data loss during the flatten/unflatten process):

Validate all language files at once:

`python ./scripts/validate_flatten_unflatten.py ./files/en.json ./output/unflat/en.unflat.json ./files/fr.json ./output/unflat/fr.unflat.json ./files/nl.json ./output/unflat/nl.unflat.json ./files/de.json ./output/unflat/de.unflat.json`

Or validate them individually:

`python ./scripts/validate_flatten_unflatten.py ./files/en.json ./output/unflat/en.unflat.json --verbose`

`python ./scripts/validate_flatten_unflatten.py ./files/fr.json ./output/unflat/fr.unflat.json --verbose`

`python ./scripts/validate_flatten_unflatten.py ./files/nl.json ./output/unflat/nl.unflat.json --verbose`

`python ./scripts/validate_flatten_unflatten.py ./files/de.json ./output/unflat/de.unflat.json --verbose`

## Extras:

### convert flat to csv:
**Files:** `FLAT_JSON` → `FLAT_CSV`

`python ./scripts/flat_to_csv.py ./output/flat/en.flat.json --out ./output/en.flat.csv`

