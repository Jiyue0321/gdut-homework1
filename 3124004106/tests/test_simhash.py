"""simhash 模块单元测试：指纹、Hamming 距离、重复率、余弦相似度。"""

from __future__ import annotations

from simhash import (
    _stable_hash,
    compute_simhash,
    cosine_rate,
    hamming_distance,
    simhash_rate,
)

# ---------- _stable_hash ----------

def test_stable_hash_deterministic():
    """同一 token 多次计算结果一致（md5 而非 hash()）。"""
    assert _stable_hash("测试") == _stable_hash("测试")


def test_stable_hash_different_tokens_differ():
    assert _stable_hash("今天") != _stable_hash("明天")


def test_stable_hash_independent_of_pythonhashseed():
    """手动校验值与已知 md5 前 8 字节一致，确保不受 PYTHONHASHSEED 影响。"""
    import hashlib
    expected = int.from_bytes(
        hashlib.md5("论文".encode()).digest()[:8], "big"
    )
    assert _stable_hash("论文") == expected


# ---------- compute_simhash ----------

def test_compute_simhash_identical_tokens_same_fingerprint():
    a = compute_simhash(["今天", "天气", "电影"])
    b = compute_simhash(["今天", "天气", "电影"])
    assert a == b


def test_compute_simhash_empty_returns_zero():
    assert compute_simhash([]) == 0


def test_compute_simhash_word_order_insensitive():
    """词频加权后，顺序不影响指纹。"""
    a = compute_simhash(["今天", "天气", "电影"])
    b = compute_simhash(["电影", "天气", "今天"])
    assert a == b


def test_compute_simhash_frequency_matters():
    """重复词改变权重 → 指纹应不同。"""
    a = compute_simhash(["今天", "天气"])
    b = compute_simhash(["今天", "今天", "天气"])
    assert a != b


def test_compute_simhash_returns_int_in_64bit_range():
    fp = compute_simhash(["a", "b", "c"])
    assert isinstance(fp, int)
    assert 0 <= fp < (1 << 64)


# ---------- hamming_distance ----------

def test_hamming_distance_identical_zero():
    assert hamming_distance(0, 0) == 0
    assert hamming_distance(123, 123) == 0


def test_hamming_distance_all_bits_differ():
    a = 0
    b = (1 << 64) - 1
    assert hamming_distance(a, b) == 64


def test_hamming_distance_known_value():
    """0b1010 ^ 0b0101 = 0b1111 → 4 位不同。"""
    assert hamming_distance(0b1010, 0b0101, bits=4) == 4


def test_hamming_distance_mask_higher_bits():
    """bits=8 时高位被屏蔽。"""
    a = 0xFF00
    b = 0x00FF
    assert hamming_distance(a, b, bits=8) == 8


# ---------- simhash_rate ----------

def test_simhash_rate_identical_is_one():
    fp = compute_simhash(["今天", "天气"])
    assert simhash_rate(fp, fp) == 1.0


def test_simhash_rate_completely_different_below_threshold():
    """全不同的指纹重复率应为 0。"""
    a = 0
    b = (1 << 64) - 1
    assert simhash_rate(a, b) == 0.0


def test_simhash_rate_assignment_sample_in_range():
    """作业样例：星期天 vs 周天，重复率应在 [0.5, 0.95] 区间。"""
    from tokenizer import tokenize
    t1 = tokenize("今天是星期天，天气晴，今天晚上我要去看电影。")
    t2 = tokenize("今天是周天，天气晴朗，我晚上要去看电影。")
    rate = simhash_rate(compute_simhash(t1), compute_simhash(t2))
    assert 0.5 <= rate <= 0.95


def test_simhash_rate_granularity_is_1_over_64():
    """64 位指纹的最小步长是 1/64 ≈ 0.0156。"""
    fp = compute_simhash(["今天"])
    rate = simhash_rate(fp, fp ^ 1)  # 翻最低位
    assert abs(rate - (1 - 1 / 64)) < 1e-9


# ---------- cosine_rate ----------

def test_cosine_rate_identical_is_one():
    tokens = ["今天", "天气", "电影"]
    assert abs(cosine_rate(tokens, tokens) - 1.0) < 1e-9


def test_cosine_rate_disjoint_vocab_is_zero():
    a = ["苹果", "香蕉"]
    b = ["桌子", "椅子"]
    assert cosine_rate(a, b) == 0.0


def test_cosine_rate_empty_returns_zero():
    assert cosine_rate([], ["a"]) == 0.0
    assert cosine_rate(["a"], []) == 0.0
    assert cosine_rate([], []) == 0.0


def test_cosine_rate_symmetric():
    a = ["今天", "天气", "电影"]
    b = ["今天", "电影", "晚上"]
    assert abs(cosine_rate(a, b) - cosine_rate(b, a)) < 1e-9


def test_cosine_rate_value_in_unit_interval():
    a = ["今天", "天气", "电影", "晚上"]
    b = ["今天", "电影", "明天"]
    r = cosine_rate(a, b)
    assert 0.0 <= r <= 1.0


def test_cosine_rate_assignment_sample():
    from tokenizer import tokenize
    t1 = tokenize("今天是星期天，天气晴，今天晚上我要去看电影。")
    t2 = tokenize("今天是周天，天气晴朗，我晚上要去看电影。")
    r = cosine_rate(t1, t2)
    assert 0.4 <= r <= 0.95
