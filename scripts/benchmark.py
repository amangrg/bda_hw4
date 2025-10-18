#!/usr/bin/env python3
from __future__ import annotations
import argparse, os, time, json, pathlib, datetime, csv
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.apriori import load_transactions, apriori, write_output

def parse_args():
    p = argparse.ArgumentParser(description="Apriori benchmark (non-overwriting metrics).")
    p.add_argument("dataset", help="Path to input dataset file")
    p.add_argument("min_support", type=int, help="Minimum support count (integer)")
    p.add_argument("--delimiter", default=None, help="Delimiter in input file (default: whitespace)")
    p.add_argument("--hash-prune", action="store_true", help="Enable hash-based candidate pruning (k=2)")
    p.add_argument("--txn-reduction", action="store_true", help="Enable transaction reduction")
    p.add_argument("--outdir", default="output", help="Output directory (default: output)")
    p.add_argument("--no-stamp", action="store_true", help="Do not timestamp the frequent-itemsets filename")
    return p.parse_args()

def make_stamp():
    return datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

def main():
    args = parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    stem = pathlib.Path(args.dataset).stem
    stamp = make_stamp()

    tag_parts = [f"{stem}", f"s{args.min_support}"]
    if args.hash_prune: tag_parts.append("hp")
    if args.txn_reduction: tag_parts.append("tr")
    tag = "_".join(tag_parts)

    out_freq = os.path.join(args.outdir, f"frequents_{tag}_{stamp}.txt")

    out_metrics = os.path.join(args.outdir, f"metrics_{tag}_{stamp}.json")
    out_summary = os.path.join(args.outdir, f"summary_{tag}_{stamp}.txt")

    hist_jsonl = os.path.join(args.outdir, "metrics_history.jsonl")
    hist_csv   = os.path.join(args.outdir, "metrics_history.csv")

    txns = load_transactions(args.dataset, delimiter=args.delimiter)
    t0 = time.perf_counter()
    frequents = apriori(txns, args.min_support,
                        use_hash_prune=args.hash_prune,
                        use_txn_reduction=args.txn_reduction)
    elapsed = time.perf_counter() - t0

    write_output(frequents, out_freq)

    counts_by_k = {}
    for fs in frequents.keys():
        k = len(fs)
        counts_by_k[k] = counts_by_k.get(k, 0) + 1

    record = {
        "timestamp": stamp,
        "dataset": args.dataset,
        "dataset_stem": stem,
        "min_support": args.min_support,
        "hash_prune": bool(args.hash_prune),
        "txn_reduction": bool(args.txn_reduction),
        "delimiter": args.delimiter,
        "n_transactions": len(txns),
        "total_frequents": len(frequents),
        "counts_by_k": {str(k): v for k, v in sorted(counts_by_k.items())},
        "runtime_seconds": elapsed,
        "frequents_file": out_freq,
    }

    with open(out_metrics, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)

    with open(out_summary, "w", encoding="utf-8") as f:
        f.write("=== Apriori Benchmark Summary ===\n")
        f.write(f"Timestamp       : {stamp}\n")
        f.write(f"Dataset         : {args.dataset}\n")
        f.write(f"Min support     : {args.min_support}\n")
        f.write(f"Hash prune      : {args.hash_prune}\n")
        f.write(f"Txn reduction   : {args.txn_reduction}\n")
        f.write(f"Transactions    : {len(txns)}\n")
        f.write(f"Runtime (sec)   : {elapsed:.4f}\n")
        f.write(f"Total frequents : {len(frequents)}\n")
        f.write("Counts by k     : " + ", ".join([f'k={k}:{v}' for k,v in sorted(counts_by_k.items())]) + "\n")
        f.write(f"Output file     : {out_freq}\n")

    with open(hist_jsonl, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

    header = ["timestamp","dataset","dataset_stem","min_support","hash_prune","txn_reduction",
              "delimiter","n_transactions","total_frequents","runtime_seconds","frequents_file","counts_by_k"]
    write_header = not os.path.exists(hist_csv)
    with open(hist_csv, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=header)
        if write_header:
            w.writeheader()
        row = dict(record)
        row["counts_by_k"] = json.dumps(record["counts_by_k"], ensure_ascii=False)
        w.writerow(row)

    print(f"Wrote frequent itemsets to: {out_freq}")
    print(f"Wrote metrics:  {out_metrics}")
    print(f"Wrote summary:  {out_summary}")
    print(f"Appended to:    {hist_jsonl} and {hist_csv}")

if __name__ == "__main__":
    main()
