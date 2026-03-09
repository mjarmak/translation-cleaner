# Translation Cleaner

## Order of operations:

### 1. flatten:
`python ./scripts/flatten_json.py ./files/en.json ./output/en.flat.json`

### 2. usage report (in project):
#### case sensitive

`python ./scripts/usage_report.py ./output/en.flat.json --src C:/Users/mjarmaka/Code/projects/gitlab/nctsp5-ui-dev/src --out ./output/usage.report.csv`

#### case insensitive
`python ./scripts/usage_report.py ./output/en.flat.json --src C:/Users/mjarmaka/Code/projects/gitlab/nctsp5-ui-dev/src --out ./output/usage-ignore-case.report.csv --ignore-case`

### 3. create mapping of duplicate keys to their canonical key:

`python ./scripts/canonical_map.py ./output/en.flat.json --duplicates-out ./output/en_duplicates.report.txt --mapping-out ./output/en_canonical-mapping.txt --prefix hash_`

### 4. rename keys (in project and translation files):
Renames keys in the project and translations, then delete duplicates in the translation files.

# REPLACE ./output/en.flat.json with real file in project
#### Apply on i18n json files

`python ./scripts/apply_mapping_flat_json.py ./output/en.flat.json ./output/en_canonical-mapping.txt`

`python ./scripts/apply_mapping_flat_json.py ./output/fr.flat.json ./output/en_canonical-mapping.txt`

`python ./scripts/apply_mapping_flat_json.py ./output/nl.flat.json ./output/en_canonical-mapping.txt`

`python ./scripts/apply_mapping_flat_json.py ./output/de.flat.json ./output/en_canonical-mapping.txt`

#### Apply on project files
`python ./scripts/apply_mapping_project.py C:/Users/mjarmaka/Code/projects/gitlab/nctsp5-ui-dev/src ./output/en_canonical-mapping.txt`

### 5. rename hashed keys (in project and translation files):
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

### 5. delete unused keys:

Manually update the output of step 2 (usage report) to create a list of keys to be removed. Save that list in `./files/remove.txt` and then run the command below.

Keep in mind that some keys are concatenated in the .ts files, such as statuses and options, so you should not those keys.

#### dry run (safe preview of what would be deleted)

`python ./scripts/delete_translations.py ./output/en.flat.json ./files/remove.txt --dry-run`

#### actual deletion

`python ./scripts/delete_translations.py ./output/en.flat.json ./files/remove.txt --out ./output/en.flat.clean.json`

### 6. unflatten:

`python ./scripts/unflatten_json.py ./output/en.flat.json --out ./output/en.unflat.json`

## Extras:

### convert flat to csv:

`python ./scripts/flat_to_csv.py ./output/en.flat.json --out ./output/en.flat.csv`

