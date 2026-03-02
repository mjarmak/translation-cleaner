# Translation Cleaner

## Order of operations:

### 1. flatten:
`python ./scripts/flatten_i18n.py ./files/en.json ./output/en.flat.json`

### 2. usage report (in project):
#### case sensitive
`python ./scripts/usage_report.py ./output/en.flat.json --src C:/Users/mjarmaka/Code/projects/gitlab/nctsp5-ui-dev/src --out ./output/usage.report.csv`

#### case insensitive
`python ./scripts/usage_report.py ./output/en.flat.json --src C:/Users/mjarmaka/Code/projects/gitlab/nctsp5-ui-dev/src --out ./output/usage-ignore-case.report.csv --ignore-case`

### 3. deduplicate:
`python ./scripts/deduplicate_keys.py ./output/en.flat.json  --duplicates-out ./output/en_duplicates.report.txt --mapping-out ./output/en_deduplicated-mapping.txt`

### 4. rename everywhere:
`python ./scripts/rename_keys.py en.flat.json hashmap.txt`

### 5. delete unused keys:

Manually update the output of step 2 (usage report) to create a list of keys to be removed. Save that list in `./files/remove.txt` and then run the command below.

Keep in mind that some keys are concatenated in the .ts files, such as statuses and options, so you should not those keys.

#### dry run (safe preview of what would be deleted)
`python delete_translations.py ./output/en.flat.json ./files/remove.txt --dry-run`

#### actual deletion
`python delete_translations.py ./output/en.flat.json ./files/remove.txt --out ./output/en.flat.clean.json`




## Extras:

### 1. convert flat to csv:
`python ./scripts/flatten_to_csv.py ./output/en.flat.json --out ./output/en.flat.csv`

