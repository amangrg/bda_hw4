#!/usr/bin/env python3
from __future__ import annotations
import argparse
from .apriori import load_transactions, apriori, write_output

def parse_args():
    p = argparse.ArgumentParser(description="Apriori frequent itemset mining")
    p.add_argument("input_file")
    p.add_argument("min_support", type=int)
    p.add_argument("output_file")
    p.add_argument("--delimiter", default=None)
    p.add_argument("--hash-prune", action="store_true")
    p.add_argument("--txn-reduction", action="store_true")
    return p.parse_args()

def main():
    args = parse_args()
    txns = load_transactions(args.input_file, delimiter=args.delimiter)
    frequents = apriori(txns, args.min_support, use_hash_prune=args.hash_prune, use_txn_reduction=args.txn_reduction)
    write_output(frequents, args.output_file)
    print(f"Wrote {len(frequents)} frequent itemsets to {args.output_file}")

if __name__ == "__main__":
    main()
