"""fileio 模块单元测试：读文本、编码回退、写答案、异常层级。"""

from __future__ import annotations

from pathlib import Path

import pytest

from exceptions import EmptyFileError, FileReadError, FileWriteError
from fileio import read_text, write_answer

# ---------- read_text ----------

def test_read_text_utf8(tmp_path: Path):
    p = tmp_path / "u.txt"
    p.write_text("今天是星期天", encoding="utf-8")
    assert read_text(str(p)) == "今天是星期天"


def test_read_text_gbk_fallback(tmp_path: Path):
    """UTF-8 strict 失败后应回退 GBK。"""
    p = tmp_path / "g.txt"
    p.write_text("今天星期天", encoding="gbk")
    assert read_text(str(p)) == "今天星期天"


def test_read_text_file_not_found_raises():
    with pytest.raises(FileReadError) as exc:
        read_text("/no/such/path/abc.txt")
    assert "不存在" in str(exc.value) or "找不到" in str(exc.value)


def test_read_text_empty_file_raises(tmp_path: Path):
    p = tmp_path / "empty.txt"
    p.write_text("", encoding="utf-8")
    with pytest.raises(EmptyFileError):
        read_text(str(p))


def test_read_text_whitespace_only_raises(tmp_path: Path):
    """strip 后为空也视为空文件。"""
    p = tmp_path / "ws.txt"
    p.write_text("   \n\t  ", encoding="utf-8")
    with pytest.raises(EmptyFileError):
        read_text(str(p))


def test_read_text_non_utf8_non_gbk_raises(tmp_path: Path):
    """既非 UTF-8 也非 GBK 的二进制应抛 FileReadError。"""
    p = tmp_path / "bin.txt"
    p.write_bytes(b"\xff\xfe\x00\x01\x02\xff")
    with pytest.raises(FileReadError) as exc:
        read_text(str(p))
    assert "编码" in str(exc.value)


def test_read_text_directory_raises(tmp_path: Path):
    """读取目录应包装为 FileReadError，而不是裸 IsADirectoryError。"""
    with pytest.raises(FileReadError):
        read_text(str(tmp_path))


# ---------- write_answer ----------

def test_write_answer_two_decimals(tmp_path: Path):
    p = tmp_path / "ans.txt"
    write_answer(str(p), 0.876)
    assert p.read_text(encoding="utf-8") == "0.88"


def test_write_answer_rounds_correctly(tmp_path: Path):
    p = tmp_path / "ans.txt"
    write_answer(str(p), 0.694)
    assert p.read_text(encoding="utf-8") == "0.69"


def test_write_answer_zero(tmp_path: Path):
    p = tmp_path / "ans.txt"
    write_answer(str(p), 0.0)
    assert p.read_text(encoding="utf-8") == "0.00"


def test_write_answer_one(tmp_path: Path):
    p = tmp_path / "ans.txt"
    write_answer(str(p), 1.0)
    assert p.read_text(encoding="utf-8") == "1.00"


def test_write_answer_to_nonexistent_dir_raises(tmp_path: Path):
    bad = tmp_path / "no_such_dir" / "ans.txt"
    with pytest.raises(FileWriteError):
        write_answer(str(bad), 0.5)
