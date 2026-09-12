"""异常层级单元测试：继承关系与可捕获性。"""

from __future__ import annotations

import pytest

from exceptions import (
    EmptyFileError,
    FileReadError,
    FileWriteError,
    InvalidArgumentError,
    PlagiarismError,
)


def test_all_exceptions_inherit_plagiarism_error():
    assert issubclass(FileReadError, PlagiarismError)
    assert issubclass(FileWriteError, PlagiarismError)
    assert issubclass(EmptyFileError, PlagiarismError)
    assert issubclass(InvalidArgumentError, PlagiarismError)


def test_invalid_argument_error_message():
    err = InvalidArgumentError("参数数量错误")
    assert "参数数量错误" in str(err)


def test_file_read_error_caught_by_base():
    """主流程用 PlagiarismError 捕获，子类必须能被基类 except 命中。"""
    with pytest.raises(PlagiarismError):
        raise FileReadError("读失败")


def test_empty_file_error_caught_by_base():
    with pytest.raises(PlagiarismError):
        raise EmptyFileError("空文件")


def test_file_write_error_caught_by_base():
    with pytest.raises(PlagiarismError):
        raise FileWriteError("写失败")


def test_empty_file_error_independent_branch():
    """EmptyFileError 与 FileReadError 并列，不是父子关系。"""
    assert not issubclass(EmptyFileError, FileReadError)
    assert not issubclass(FileReadError, EmptyFileError)
