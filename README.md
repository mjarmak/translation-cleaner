# Translation Cleaner

### Order of operations:

#### 1. flatten:
`python ./scripts/flatten_i18n.py ./files/en.json ./output/en.flat.json`

#### 2. usage report:
`python ./scripts/usage_report.py ./output/en.flat.json --src C:/Users/mjarmaka/Code/projects/gitlab/nctsp5-ui-dev/src --out ./output/usage.csv`

#### 3 deduplicate:
`python ./scripts/deduplicate_keys.py en.flat.json`

#### 4 rename everywhere:
`python ./scripts/rename_keys.py en.flat.json hashmap.txt`