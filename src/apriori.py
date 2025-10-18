from __future__ import annotations
from collections import defaultdict
from typing import List, Set, Dict, FrozenSet, Optional, Tuple

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

def write_output(frequents: Dict[FrozenSet[str], int], path: str) -> None:
    def key_func(it):
        items, sup = sorted(list(it[0])), it[1]
        return (len(items), items, -sup)
    with open(path, "w", encoding="utf-8") as f:
        for itemset, sup in sorted(frequents.items(), key=key_func):
            f.write("{} ({})\n".format(" ".join(sorted(itemset)), sup))

def initial_L1(transactions: List[Set[str]], min_support: int) -> Dict[FrozenSet[str], int]:
    counts: Dict[str, int] = defaultdict(int)
    for t in transactions:
        for item in t:
            counts[item] += 1
    return {frozenset([i]): c for i, c in counts.items() if c >= min_support}

def _items_in_L(prev_L: Dict[FrozenSet[str], int]) -> Set[str]:
    keep: Set[str] = set()
    for s in prev_L.keys():
        keep |= set(s)
    return keep

def generate_candidates(prev_L: Dict[FrozenSet[str], int], k: int):
    prev_sets = list(prev_L.keys())
    candidates = set()
    n = len(prev_sets)
    for i in range(n):
        for j in range(i+1, n):
            a, b = prev_sets[i], prev_sets[j]
            u = a | b
            if len(u) == k:
                candidates.add(frozenset(u))
    return candidates

def has_infrequent_subset(candidate: FrozenSet[str], prev_L: Dict[FrozenSet[str], int]) -> bool:
    for item in candidate:
        if frozenset(candidate - {item}) not in prev_L:
            return True
    return False

def prune_candidates(candidates, prev_L):
    return {c for c in candidates if not has_infrequent_subset(c, prev_L)}

def count_support_and_matched(candidates, transactions, k: int) -> Tuple[Dict[FrozenSet[str], int], Set[int]]:
    counts = {c: 0 for c in candidates}
    matched: Set[int] = set()
    for idx, t in enumerate(transactions):
        if len(t) < k:
            continue
        hit = False
        for c in candidates:
            if c.issubset(t):
                counts[c] += 1
                hit = True
        if hit:
            matched.add(idx)
    return counts, matched

def hash_prune_pairs(transactions: List[Set[str]], min_support: int, frequent_items: Set[str], avg_txn_len: float, num_buckets: int = 100_003, pre_len_threshold: int = 10, max_expected_keep: float = 0.60) -> Optional[Set[FrozenSet[str]]]:
    if not frequent_items or avg_txn_len < pre_len_threshold:
        return None
    items_sorted = sorted(frequent_items)
    item_to_id = {item: idx for idx, item in enumerate(items_sorted)}
    buckets = [0] * num_buckets
    touched = 0
    for t in transactions:
        ids = [item_to_id[it] for it in t if it in item_to_id]
        m = len(ids)
        if m < 2:
            continue
        ids.sort()
        for i in range(m):
            ai = ids[i]
            for j in range(i+1, m):
                bj = ids[j]
                h = (ai * 1315423911 + bj * 2654435761) % num_buckets
                if buckets[h] == 0:
                    touched += 1
                buckets[h] += 1
    if touched == 0:
        return set()
    freq_bucket = sum(1 for b in buckets if b >= min_support)
    frac_freq = freq_bucket / touched
    if frac_freq > max_expected_keep:
        return None
    C2: Set[FrozenSet[str]] = set()
    for t in transactions:
        ids = [item_to_id[it] for it in t if it in item_to_id]
        m = len(ids)
        if m < 2:
            continue
        ids.sort()
        for i in range(m):
            ai = ids[i]
            for j in range(i+1, m):
                bj = ids[j]
                h = (ai * 1315423911 + bj * 2654435761) % num_buckets
                if buckets[h] >= min_support:
                    a = items_sorted[ai]; b = items_sorted[bj]
                    C2.add(frozenset((a, b)))
    return C2

def reduce_transactions(transactions: List[Set[str]], matched_idxs: Set[int], keep_items: Set[str], min_len: int) -> List[Set[str]]:
    reduced = []
    for i, t in enumerate(transactions):
        if i in matched_idxs:
            x = t & keep_items
            if len(x) >= min_len:
                reduced.append(x)
    return reduced

def apriori(transactions, min_support, use_hash_prune: bool = False, use_txn_reduction: bool = False):
    Lk = initial_L1(transactions, min_support)
    if not Lk:
        return {}
    all_frequents = dict(Lk)
    k = 2
    n_tx = len(transactions)
    avg_len = sum(len(t) for t in transactions) / n_tx if n_tx else 0.0
    while Lk:
        if k == 2 and use_hash_prune:
            keep1 = _items_in_L(Lk)
            Ck = hash_prune_pairs(transactions, min_support, keep1, avg_len)
            if Ck is None:
                Ck = prune_candidates(generate_candidates(Lk, k), Lk)
            else:
                Ck = prune_candidates(Ck, Lk)
        else:
            Ck = prune_candidates(generate_candidates(Lk, k), Lk)
        if not Ck:
            break
        counts, matched = count_support_and_matched(Ck, transactions, k)
        Lk = {c: cnt for c, cnt in counts.items() if cnt >= min_support}
        all_frequents.update(Lk)
        if not Lk:
            break
        k += 1
        if use_txn_reduction and n_tx > 5000:
            keepk = _items_in_L(Lk)
            frac = len(matched) / n_tx if n_tx else 1.0
            if frac < 0.95:
                transactions = reduce_transactions(transactions, matched, keepk, k)
                n_tx = len(transactions)
                avg_len = sum(len(t) for t in transactions) / n_tx if n_tx else 0.0
    return all_frequents
