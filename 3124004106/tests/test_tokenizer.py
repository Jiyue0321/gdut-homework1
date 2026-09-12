"""tokenizer 模块单元测试：分词、去标点、小写化。"""

from __future__ import annotations

from tokenizer import _is_punctuation, tokenize

# ---------- _is_punctuation ----------

def test_is_punctuation_empty_returns_true():
    assert _is_punctuation("") is True


def test_is_punctuation_chinese_punct_true():
    assert _is_punctuation("，") is True
    assert _is_punctuation("。") is True
    assert _is_punctuation("！") is True
    assert _is_punctuation("？") is True


def test_is_punctuation_ascii_punct_true():
    assert _is_punctuation(",") is True
    assert _is_punctuation(".") is True
    assert _is_punctuation("!") is True
    assert _is_punctuation("@") is True


def test_is_punctuation_fullwidth_true():
    assert _is_punctuation("：") is True
    assert _is_punctuation("（") is True


def test_is_punctuation_chinese_char_false():
    assert _is_punctuation("今") is False
    assert _is_punctuation("天") is False


def test_is_punctuation_mixed_returns_false():
    """只要有一个非标点字符就返回 False。"""
    assert _is_punctuation("，今天") is False


def test_is_punctuation_whitespace_only_true():
    assert _is_punctuation("   ") is True
    assert _is_punctuation("\n\t") is True


# ---------- tokenize ----------

def test_tokenize_strips_punctuation():
    result = tokenize("今天，天气。")
    assert result == ["今天", "天气"]


def test_tokenize_lowercase_ascii():
    """jieba 对中英混排的切分：Python 保留为词，真好被切成一个词。"""
    result = tokenize("Python真好")
    assert "python" in result
    assert "真好" in result


def test_tokenize_empty_string():
    assert tokenize("") == []


def test_tokenize_only_punctuation():
    assert tokenize("，。！？   \n") == []


def test_tokenize_preserves_word_frequency():
    result = tokenize("今天今天今天")
    assert result == ["今天", "今天", "今天"]


def test_tokenize_mixed_cn_en_punct():
    result = tokenize("Hello, 世界！今天 weather 晴。")
    assert "hello" in result
    assert "世界" in result
    assert "今天" in result
    assert "weather" in result
    assert "晴" in result
    assert "," not in result
    assert "！" not in result


def test_tokenize_whitespace_inside_token_stripped():
    """jieba 可能切出带空格的片段，应被 strip 清理。"""
    result = tokenize("今天  天气")
    assert result == ["今天", "天气"]


def test_tokenize_fullwidth_letters():
    """全角字母应能被处理（jieba 通常会保留）。"""
    result = tokenize("ＡＢＣ今天")
    assert "今天" in result
    assert len(result) >= 1
