# Translation Cleaner

## File Variables

```
INPUT_FILE = ./files/en.json
FLAT_JSON = ./output/en.flat.json
FLAT_JSON_FR = ./output/fr.flat.json
FLAT_JSON_NL = ./output/nl.flat.json
FLAT_JSON_DE = ./output/de.flat.json
USAGE_REPORT = ./output/usage.report.csv
USAGE_REPORT_IGNORE_CASE = ./output/usage-ignore-case.report.csv
DUPLICATES_REPORT = ./output/en_duplicates.report.txt
CANONICAL_MAPPING = ./output/en_canonical-mapping.txt
CANONICAL_MAPPING_JSON = ./output/en_canonical-mapping.json
HASH_RENAME_MAPPING = ./output/hash_rename-mapping.txt
REMOVE_LIST = ./files/remove.txt
FLAT_JSON_CLEAN = ./output/en.flat.clean.json
UNFLAT_JSON = ./output/en.unflat.json
FLAT_CSV = ./output/en.flat.csv
PROJECT_SRC = C:/Users/mjarmaka/Code/projects/gitlab/nctsp5-ui-dev/src
```

## Order of operations:

### 1. flatten:
**Files:** `INPUT_FILE` + `FLAT_JSON_FR` + `FLAT_JSON_NL` + `FLAT_JSON_DE` → All flattened outputs

Flatten all language files at once:
`python ./scripts/flatten_json.py ./files/en.json ./output/en.flat.json ./files/fr.json ./output/fr.flat.json ./files/nl.json ./output/nl.flat.json ./files/de.json ./output/de.flat.json`

Or flatten them individually:
`python ./scripts/flatten_json.py ./files/en.json ./output/en.flat.json`

`python ./scripts/flatten_json.py ./files/fr.json ./output/fr.flat.json`

`python ./scripts/flatten_json.py ./files/nl.json ./output/nl.flat.json`

`python ./scripts/flatten_json.py ./files/de.json ./output/de.flat.json`

### 2. usage report (in project):
**Files:** `FLAT_JSON` → `USAGE_REPORT` or `USAGE_REPORT_IGNORE_CASE`

#### case sensitive, case insensitive:
`python ./scripts/usage_report.py ./output/en.flat.json --src C:/Users/mjarmaka/Code/projects/gitlab/nctsp5-ui-dev/src --out ./output/usage.report.csv`,

`python ./scripts/usage_report.py ./output/en.flat.json --src C:/Users/mjarmaka/Code/projects/gitlab/nctsp5-ui-dev/src --out ./output/usage-ignore-case.report.csv --ignore-case`

#### case sensitive with language values, case insensitive with language values:
`python ./scripts/usage_report.py ./output/en.flat.json --src C:/Users/mjarmaka/Code/projects/gitlab/nctsp5-ui-dev/src --out ./output/usage.report.csv --languages "./output/fr.flat.json,./output/nl.flat.json,./output/de.flat.json"`,

`python ./scripts/usage_report.py ./output/en.flat.json --src C:/Users/mjarmaka/Code/projects/gitlab/nctsp5-ui-dev/src --out ./output/usage-ignore-case.report.csv --ignore-case --languages "./output/fr.flat.json,./output/nl.flat.json,./output/de.flat.json"`

### 3. create mapping of duplicate keys to their canonical key:
**Files:** `FLAT_JSON` → `CANONICAL_MAPPING` + `DUPLICATES_REPORT`

#### case sensitive

`python ./scripts/canonical_map.py ./output/en.flat.json --duplicates-out ./output/en_duplicates.report.txt --mapping-out ./output/en_canonical-mapping.txt --prefix hash_`

#### case insensitive
`python ./scripts/canonical_map.py ./output/en.flat.json --duplicates-out ./output/en_duplicates.report.txt --mapping-out ./output/en_canonical-mapping.txt --prefix hash_ --ignore-case`

### 4. rename keys (in project and translation files):
Renames keys in the project and translations, then delete duplicates in the translation files.

# REPLACE `FLAT_JSON` with real file in project
#### Apply on i18n json files

`python ./scripts/apply_mapping_flat_json.py ./output/en.flat.json ./output/en_canonical-mapping.txt`

`python ./scripts/apply_mapping_flat_json.py ./output/fr.flat.json ./output/en_canonical-mapping.txt`

`python ./scripts/apply_mapping_flat_json.py ./output/nl.flat.json ./output/en_canonical-mapping.txt`

`python ./scripts/apply_mapping_flat_json.py ./output/de.flat.json ./output/en_canonical-mapping.txt`

#### Apply on project files
`python ./scripts/apply_mapping_project.py C:/Users/mjarmaka/Code/projects/gitlab/nctsp5-ui-dev/src ./output/en_canonical-mapping.txt`

### 5. rename hashed keys (in project and translation files):
**Files:** `CANONICAL_MAPPING_JSON` → `HASH_RENAME_MAPPING` → `FLAT_JSON*`

Run the following scripts to create a mapping file for the hashed keys in the 'common.<key>' format. The hashed keys are identified by looking at the 'hash_' prefix in the key names.

`python ./scripts/rename_hashed_keys.py ./output/en_canonical-mapping.json ./output/hash_rename-mapping.txt --prefix hash_`

#### Apply on i18n json files
Then run the rename script below again to update the project and translation files.

`python ./scripts/apply_mapping_flat_json.py ./output/en.flat.json ./output/hash_rename-mapping.txt`

`python ./scripts/apply_mapping_flat_json.py ./output/fr.flat.json ./output/hash_rename-mapping.txt`

`python ./scripts/apply_mapping_flat_json.py ./output/nl.flat.json ./output/hash_rename-mapping.txt`

`python ./scripts/apply_mapping_flat_json.py ./output/de.flat.json ./output/hash_rename-mapping.txt`

#### Apply on project files
`python ./scripts/apply_mapping_project.py C:/Users/mjarmaka/Code/projects/gitlab/nctsp5-ui-dev/src ./output/hash_rename-mapping.txt`

### 6. delete unused keys:
**Files:** `FLAT_JSON` + `REMOVE_LIST` → `FLAT_JSON_CLEAN`

Manually update the output of step 2 (usage report) to create a list of keys to be removed. Save that list in `REMOVE_LIST` and then run the command below.

Keep in mind that some keys are concatenated in the .ts files, such as statuses and options, so you should not those keys.

#### dry run (safe preview of what would be deleted)

`python ./scripts/delete_translations.py ./output/en.flat.json ./files/remove.txt --dry-run`

#### actual deletion

`python ./scripts/delete_translations.py ./output/en.flat.json ./files/remove.txt --out ./output/en.flat.clean.json`

### 7. unflatten:
**Files:** `FLAT_JSON` + `FLAT_JSON_FR` + `FLAT_JSON_NL` + `FLAT_JSON_DE` → All unflattened outputs

Unflatten all language files at once:

`python ./scripts/unflatten_json.py ./output/en.flat.json ./output/en.unflat.json ./output/fr.flat.json ./output/fr.unflat.json ./output/nl.flat.json ./output/nl.unflat.json ./output/de.flat.json ./output/de.unflat.json`

Or unflatten them individually:

`python ./scripts/unflatten_json.py ./output/en.flat.json ./output/en.unflat.json`

`python ./scripts/unflatten_json.py ./output/fr.flat.json ./output/fr.unflat.json`

`python ./scripts/unflatten_json.py ./output/nl.flat.json ./output/nl.unflat.json`

`python ./scripts/unflatten_json.py ./output/de.flat.json ./output/de.unflat.json`

## Extras:

### convert flat to csv:
**Files:** `FLAT_JSON` → `FLAT_CSV`

`python ./scripts/flat_to_csv.py ./output/en.flat.json --out ./output/en.flat.csv`

