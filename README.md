# Translation Cleaner

### Order of operations:

#### 1. flatten:
`python ./scripts/flatten_i18n.py ./in/en.json ./out/en.flat.json`

#### 2. usage report:
`python ./scripts/usage_report.py en.flat.json`

#### 3 deduplicate:
`python ./scripts/deduplicate_keys.py en.flat.json`

#### 4 rename everywhere:
`python ./scripts/rename_keys.py en.flat.json hashmap.txt`