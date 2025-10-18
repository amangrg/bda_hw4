# Apriori Frequent Itemset Mining (CLI)

This project implements the classic **Apriori** algorithm (Agrawal & Srikant) for mining frequent itemsets.
It supports two optional optimizations:
- **Hash-based candidate pruning** for 2-itemsets
- **Transaction reduction** across iterations

## Requirements
- Python 3.9+
- No external packages required

## Project Layout
```
apriori_project/
├─ src/
│  ├─ __init__.py
│  ├─ apriori.py
│  └─ main.py              # CLI entrypoint
├─ sample_data/
│  └─ toy_transactions.txt
├─ output/
├─ scripts/
│  ├─ run_apriori.sh
│  └─ run_apriori.bat
├─ tests/
│  └─ test_apriori.py
├─ REPORT_TEMPLATE.md
└─ README.md
```

## Input Format
- One transaction **per line**.
- Items separated by **whitespace** by default (use `--delimiter` to change).

Example (`sample_data/toy_transactions.txt`):
```
A B C
A C
B C D
A B D
B E
```

## Build/Run
From the project root:

```bash
# Option 1: Python module
python -m src.main sample_data/toy_transactions.txt 2 output/frequents.txt

# With optimizations
python -m src.main sample_data/toy_transactions.txt 2 output/frequents.txt --hash-prune --txn-reduction

# Specify delimiter (e.g., comma)
python -m src.main path/to/your.csv 100 output/out.txt --delimiter ","
```

On Windows (PowerShell/CMD), you can run:
```bat
scripts\run_apriori.bat
```

On Mac/Linux:
```bash
bash scripts/run_apriori.sh
```

## Output Format
Each line contains a frequent itemset and its **support count** in parentheses, e.g.:
```
A B C (5)
```
meaning itemset `{A, B, C}` has support count **5**.

The file is sorted by: (itemset size, lexicographic items, support descending).

## Notes on Optimizations
- **Hash-based pair pruning**: uses a large-bucket hash to eliminate 2-itemset candidates whose buckets fall below the minimum support.
- **Transaction reduction**: after computing `L_k`, transactions that contain **no** frequent `k`-itemset are dropped for the next iteration.

Both are optional flags and preserve correctness (they only prune candidates/transactions that cannot produce frequent supersets).

## Testing
```bash
python -m pytest -q
```

## Datasets
You can test on FIMI datasets (http://fimi.ua.ac.be/data/) or those in WEKA/R/Mahout.
For large datasets, start with higher min-support to validate correctness and then decrease.

## Reproducibility
- Record the exact **min_support** and **dataset** used.
- Save the produced `output/frequents.txt` for submission.
- Include the filled-in `REPORT_TEMPLATE.md` (export to PDF).

## License
MIT
