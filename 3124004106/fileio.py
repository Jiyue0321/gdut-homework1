"""文件读写封装：UTF-8 优先、GBK 回退，统一异常出口。"""

from __future__ import annotations

from exceptions import EmptyFileError, FileReadError, FileWriteError

_UTF8_ERRORS_TO_TRY = ("utf-8", "gbk")


def read_text(path: str) -> str:
    """读取文本文件，UTF-8 strict 失败则回退 GBK。

    - 文件不存在/无权限 → FileReadError
    - UTF-8/GBK 都解不了 → FileReadError
    - 内容为空字符串 → EmptyFileError
    """
    try:
        with open(path, "r", encoding=_UTF8_ERRORS_TO_TRY[0]) as f:
            text = f.read()
    except FileNotFoundError as e:
        raise FileReadError(f"文件不存在: {path}") from e
    except PermissionError as e:
        raise FileReadError(f"无读取权限: {path}") from e
    except UnicodeDecodeError:
        try:
            with open(path, "r", encoding=_UTF8_ERRORS_TO_TRY[1]) as f:
                text = f.read()
        except UnicodeDecodeError as e:
            raise FileReadError(f"编码无法识别（已尝试 UTF-8/GBK）: {path}") from e
        except OSError as e:
            raise FileReadError(f"读取失败: {path}: {e}") from e
    except OSError as e:
        raise FileReadError(f"读取失败: {path}: {e}") from e

    if not text.strip():
        raise EmptyFileError(f"文件内容为空: {path}")
    return text


def write_answer(path: str, rate: float) -> None:
    """将重复率以两位小数写入答案文件。"""
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"{rate:.2f}")
    except OSError as e:
        raise FileWriteError(f"写入失败: {path}: {e}") from e
