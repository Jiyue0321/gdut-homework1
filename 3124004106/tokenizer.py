"""中文分词封装：jieba 切词 + 标点/空白过滤。"""

from __future__ import annotations

import unicodedata

from jieba import lcut

# Unicode 通用标点区段 + CJK 标点区段，覆盖中英文常见标点。
_PUNCT_RANGES = (
    (0x0021, 0x002F),  # ASCII 标点 ! " # ... /
    (0x003A, 0x0040),  # ASCII 标点 : ; < = > ? @
    (0x005B, 0x0060),  # ASCII 标点 [ \ ] ^ _ `
    (0x007B, 0x007E),  # ASCII 标点 { | } ~
    (0x2000, 0x206F),  # 通用标点
    (0x3000, 0x303F),  # CJK 标点
    (0xFF00, 0xFFEF),  # 全角字符
)


def _is_punctuation(token: str) -> bool:
    """判断 token 是否全是标点/空白/不可见字符。"""
    if not token:
        return True
    for ch in token:
        if ch.isspace():
            continue
        cp = ord(ch)
        cat = unicodedata.category(ch)
        if cat.startswith("P"):
            continue
        if any(lo <= cp <= hi for lo, hi in _PUNCT_RANGES):
            continue
        return False
    return True


def tokenize(text: str) -> list[str]:
    """jieba 分词后过滤标点/空白，拉丁字母小写化。

    纯标点输入返回空列表，由上层特判为 0.00 重复率。
    """
    tokens = lcut(text)
    result: list[str] = []
    for tok in tokens:
        if _is_punctuation(tok):
            continue
        cleaned = tok.strip()
        if not cleaned:
            continue
        result.append(cleaned.lower())
    return result
