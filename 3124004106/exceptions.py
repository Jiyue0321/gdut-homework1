"""自定义异常层级，统一查重流程的错误出口。"""

from __future__ import annotations


class PlagiarismError(Exception):
    """查重工具所有自定义异常的基类。"""


class InvalidArgumentError(PlagiarismError):
    """命令行参数数量或格式不合法。"""


class FileReadError(PlagiarismError):
    """原文或抄袭版文件读取失败：不存在、无权限或编码无法识别。"""


class FileWriteError(PlagiarismError):
    """答案文件写入失败：目录不存在或无写权限。"""


class EmptyFileError(PlagiarismError):
    """文件存在但内容为空字符串，无任何字符可查重。"""
