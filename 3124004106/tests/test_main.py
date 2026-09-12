"""main 模块集成测试：参数解析、端到端、异常路径。"""

from __future__ import annotations

from pathlib import Path

import pytest

from exceptions import InvalidArgumentError
from main import main, parse_args

# ---------- parse_args ----------

def test_parse_args_three_paths_default_method():
    orig, plag, ans, method = parse_args(["a.txt", "b.txt", "c.txt"])
    assert (orig, plag, ans, method) == ("a.txt", "b.txt", "c.txt", "simhash")


def test_parse_args_too_few_raises():
    with pytest.raises(InvalidArgumentError):
        parse_args(["a.txt", "b.txt"])


def test_parse_args_too_many_raises():
    with pytest.raises(InvalidArgumentError):
        parse_args(["a.txt", "b.txt", "c.txt", "d.txt"])


def test_parse_args_zero_raises():
    with pytest.raises(InvalidArgumentError):
        parse_args([])


def test_parse_args_method_cosine():
    orig, plag, ans, method = parse_args(
        ["--method", "cosine", "a.txt", "b.txt", "c.txt"]
    )
    assert method == "cosine"


def test_parse_args_method_default_simhash():
    orig, plag, ans, method = parse_args(
        ["--method", "simhash", "a.txt", "b.txt", "c.txt"]
    )
    assert method == "simhash"


def test_parse_args_method_case_insensitive():
    _, _, _, method = parse_args(
        ["--method", "COSINE", "a.txt", "b.txt", "c.txt"]
    )
    assert method == "cosine"


def test_parse_args_unknown_method_raises():
    with pytest.raises(InvalidArgumentError) as exc:
        parse_args(["--method", "levenshtein", "a.txt", "b.txt", "c.txt"])
    assert "未知算法" in str(exc.value)


def test_parse_args_method_no_value_raises():
    with pytest.raises(InvalidArgumentError):
        parse_args(["--method"])


def test_parse_args_method_missing_paths_raises():
    with pytest.raises(InvalidArgumentError):
        parse_args(["--method", "cosine", "a.txt"])


# ---------- main 端到端 ----------

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def test_main_end_to_end_simhash(tmp_path: Path):
    ans = tmp_path / "ans.txt"
    rc = main([
        str(FIXTURES / "orig.txt"),
        str(FIXTURES / "orig_add.txt"),
        str(ans),
    ])
    assert rc == 0
    text = ans.read_text(encoding="utf-8")
    assert len(text) == 4
    assert text[0] == "0" or text[0] == "1"
    rate = float(text)
    assert 0.5 <= rate <= 0.95


def test_main_end_to_end_cosine(tmp_path: Path):
    ans = tmp_path / "ans.txt"
    rc = main([
        "--method", "cosine",
        str(FIXTURES / "orig.txt"),
        str(FIXTURES / "orig_add.txt"),
        str(ans),
    ])
    assert rc == 0
    rate = float(ans.read_text(encoding="utf-8"))
    assert 0.4 <= rate <= 0.95


def test_main_identical_files_rate_one(tmp_path: Path):
    """完全相同文本应得 1.00。"""
    ans = tmp_path / "ans.txt"
    rc = main([
        str(FIXTURES / "orig.txt"),
        str(FIXTURES / "orig.txt"),
        str(ans),
    ])
    assert rc == 0
    assert ans.read_text(encoding="utf-8") == "1.00"


def test_main_empty_file_returns_zero(tmp_path: Path):
    """空文件 → EmptyFileError 被捕获 → 退出码 1。"""
    ans = tmp_path / "ans.txt"
    rc = main([
        str(FIXTURES / "empty.txt"),
        str(FIXTURES / "orig.txt"),
        str(ans),
    ])
    assert rc == 1


def test_main_only_punctuation_returns_zero(tmp_path: Path):
    """纯标点输入 → tokens 为空 → 特判 0.00。"""
    ans = tmp_path / "ans.txt"
    rc = main([
        str(FIXTURES / "only_punct.txt"),
        str(FIXTURES / "orig.txt"),
        str(ans),
    ])
    assert rc == 0
    assert ans.read_text(encoding="utf-8") == "0.00"


def test_main_file_not_found_returns_one(tmp_path: Path, capsys):
    ans = tmp_path / "ans.txt"
    rc = main([
        "/no/such/orig.txt",
        str(FIXTURES / "orig_add.txt"),
        str(ans),
    ])
    assert rc == 1
    captured = capsys.readouterr()
    assert "错误" in captured.err


def test_main_insufficient_args_returns_one(capsys):
    rc = main(["only_one.txt"])
    assert rc == 1
    captured = capsys.readouterr()
    assert "错误" in captured.err


def test_main_non_utf8_file_returns_one(tmp_path: Path):
    ans = tmp_path / "ans.txt"
    rc = main([
        str(FIXTURES / "non_utf8.txt"),
        str(FIXTURES / "orig.txt"),
        str(ans),
    ])
    assert rc == 1


def test_main_unknown_method_returns_one(tmp_path: Path, capsys):
    ans = tmp_path / "ans.txt"
    rc = main([
        "--method", "unknown",
        str(FIXTURES / "orig.txt"),
        str(FIXTURES / "orig_add.txt"),
        str(ans),
    ])
    assert rc == 1
    assert "未知算法" in capsys.readouterr().err


def test_main_answer_format_two_decimals(tmp_path: Path):
    """答案文件必须是两位小数浮点。"""
    ans = tmp_path / "ans.txt"
    rc = main([
        str(FIXTURES / "orig.txt"),
        str(FIXTURES / "orig_mod.txt"),
        str(ans),
    ])
    assert rc == 0
    text = ans.read_text(encoding="utf-8")
    assert text.count(".") == 1
    assert len(text.split(".")[1]) == 2
