"""SimHash 指纹计算与 Hamming 距离归一化。"""

from __future__ import annotations

import hashlib
from collections import Counter


def _stable_hash(token: str) -> int:
    """返回 token 的 64 位稳定哈希（md5 前 8 字节）。

    用 md5 而非内置 hash()，避免 PYTHONHASHSEED 随机化，
    保证同一输入在不同进程中指纹一致。
    """
    digest = hashlib.md5(token.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


def compute_simhash(tokens: list[str], bits: int = 64) -> int:
    """对 token 列表计算 SimHash 指纹。

    词频加权：每个词权重为其出现次数。逐位累加 ± 权重，
    最终按符号位定结果（>0 → 1，≤0 → 0）。
    空 token 列表返回 0，由上层特判为 0.00 重复率。
    """
    if not tokens:
        return 0

    weights = Counter(tokens)
    vector = [0] * bits
    for token, weight in weights.items():
        h = _stable_hash(token)
        for i in range(bits):
            if h & (1 << i):
                vector[i] += weight
            else:
                vector[i] -= weight

    fingerprint = 0
    for i in range(bits):
        if vector[i] > 0:
            fingerprint |= 1 << i
    return fingerprint


def hamming_distance(a: int, b: int, bits: int = 64) -> int:
    """两个指纹的 Hamming 距离（不同位个数）。"""
    mask = (1 << bits) - 1
    return bin((a ^ b) & mask).count("1")


def simhash_rate(a: int, b: int, bits: int = 64) -> float:
    """由 SimHash 指纹计算归一化重复率：1 - hamming / bits。"""
    return 1.0 - hamming_distance(a, b, bits) / bits


def cosine_rate(tokens_a: list[str], tokens_b: list[str]) -> float:
    """TF 向量余弦相似度，作为 SimHash 之外的对照算法。

    两侧都空或一侧无词时返回 0.0，避免零向量除零。
    """
    if not tokens_a or not tokens_b:
        return 0.0

    ca = Counter(tokens_a)
    cb = Counter(tokens_b)
    common = ca.keys() & cb.keys()
    if not common:
        return 0.0

    dot = sum(ca[t] * cb[t] for t in common)
    norm_a = sum(v * v for v in ca.values()) ** 0.5
    norm_b = sum(v * v for v in cb.values()) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)
