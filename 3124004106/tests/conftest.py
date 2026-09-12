"""pytest 共享 fixture：测试用临时文本文件。"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# 让 tests/ 能 import 到上一层的模块
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def tmp_text(tmp_path: Path) -> Path:
    """临时写入一句中文，返回路径。"""
    p = tmp_path / "in.txt"
    p.write_text("今天是星期天，天气晴。", encoding="utf-8")
    return p


@pytest.fixture
def fixtures_dir() -> Path:
    return Path(__file__).resolve().parent / "fixtures"
