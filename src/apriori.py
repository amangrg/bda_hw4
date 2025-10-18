from __future__ import annotations
from collections import defaultdict
from typing import List, Set, Dict, FrozenSet, Optional

def load_transactions(path: str, delimiter: Optional[str] = None) -> List[Set[str]]:
    txns: List[Set[str]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: 
                continue
            items = line.split(delimiter) if delimiter is not None else line.split()
            items = [it for it in items if it != ""]
            if items:
                txns.append(set(items))
    return txns

def initial_L1(transactions: List[Set[str]], min_support: int) -> Dict[FrozenSet[str], int]:
    counts = defaultdict(int)
    for t in transactions:
        for item in t:
            counts[item] += 1
    return {frozenset([i]): c for i, c in counts.items() if c >= min_support}

def generate_candidates(prev_L: Dict[FrozenSet[str], int], k: int):
    prev_sets = list(prev_L.keys())
    candidates = set()
    n = len(prev_sets)
    for i in range(n):
        for j in range(i+1, n):
            a, b = prev_sets[i], prev_sets[j]
            union = a | b
            if len(union) == k:
                candidates.add(frozenset(union))
    return candidates

def has_infrequent_subset(candidate: FrozenSet[str], prev_L: Dict[FrozenSet[str], int]) -> bool:
    for item in candidate:
        if frozenset(candidate - {item}) not in prev_L:
            return True
    return False

def prune_candidates(candidates, prev_L):
    return {c for c in candidates if not has_infrequent_subset(c, prev_L)}

def count_support(candidates, transactions):
    counts = {c: 0 for c in candidates}
    for t in transactions:
        for c in candidates:
            if c.issubset(t):
                counts[c] += 1
    return counts

def hash_prune_pairs(transactions, min_support, num_buckets=100003):
    items_sorted = sorted({i for t in transactions for i in t})
    item_to_id = {item: idx for idx, item in enumerate(items_sorted)}
    buckets = [0]*num_buckets
    for t in transactions:
        items = sorted(t, key=lambda x: item_to_id[x])
        for i in range(len(items)):
            for j in range(i+1, len(items)):
                a, b = items[i], items[j]
                h = (item_to_id[a]*1315423911 + item_to_id[b]*2654435761) % num_buckets
                buckets[h] += 1
    candidates = set()
    for t in transactions:
        items = sorted(t, key=lambda x: item_to_id[x])
        for i in range(len(items)):
            for j in range(i+1, len(items)):
                a, b = items[i], items[j]
                h = (item_to_id[a]*1315423911 + item_to_id[b]*2654435761) % num_buckets
                if buckets[h] >= min_support:
                    candidates.add(frozenset([a,b]))
    return candidates

def reduce_transactions(transactions, frequent_itemsets_k):
    if not frequent_itemsets_k:
        return transactions
    Lk = set(frequent_itemsets_k.keys())
    reduced = []
    for t in transactions:
        if any(l.issubset(t) for l in Lk):
            reduced.append(t)
    return reduced

def apriori(transactions, min_support, use_hash_prune=False, use_txn_reduction=False):
    Lk = initial_L1(transactions, min_support)
    all_frequents = dict(Lk)
    k = 2
    current_txns = transactions

    while Lk:
        if k == 2 and use_hash_prune:
            Ck = prune_candidates(hash_prune_pairs(current_txns, min_support), Lk)
        else:
            Ck = prune_candidates(generate_candidates(Lk, k), Lk)
        if not Ck:
            break
        counts = count_support(Ck, current_txns)
        Lk = {c: cnt for c, cnt in counts.items() if cnt >= min_support}
        all_frequents.update(Lk)
        if use_txn_reduction:
            current_txns = reduce_transactions(current_txns, Lk)
        k += 1
    return all_frequents

def write_output(frequents, path):
    def key_func(it):
        items, sup = sorted(list(it[0])), it[1]
        return (len(items), items, -sup)
    lines = []
    for itemset, sup in sorted(frequents.items(), key=key_func):
        lines.append("{} ({})".format(" ".join(sorted(itemset)), sup))
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
