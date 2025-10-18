# Apriori Frequent Itemset Mining (CLI)

This project implements the classic **Apriori** algorithm (Agrawal & Srikant) for mining frequent itemsets.
It supports two optional optimizations:
- **Hash-based candidate pruning** for 2-itemsets
- **Transaction reduction** across iterations

## Requirements
- Python 3.9+
- No external packages required

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
python scripts\benchmark.py data\chess.dat 2600

# With optimizations
python scripts\benchmark.py data\chess.dat 2600 --hash-prune --txn-reduction

On Windows (PowerShell/CMD), you can run:
```bat
scripts\run.ps1
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

## Datasets
You can test on FIMI datasets (http://fimi.ua.ac.be/data/) 

## License
MIT
