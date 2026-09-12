"""论文查重命令行入口：读文件 → 分词 → SimHash/余弦 → 重复率 → 写答案。"""

from __future__ import annotations

import sys

from exceptions import InvalidArgumentError, PlagiarismError
from fileio import read_text, write_answer
from simhash import compute_simhash, cosine_rate, simhash_rate
from tokenizer import tokenize

_METHODS = ("simhash", "cosine")


def parse_args(argv: list[str]) -> tuple[str, str, str, str]:
    """校验命令行参数：可选 --method，再跟 3 个路径。

    支持两种形式：
        orig plag ans              （默认 simhash）
        --method cosine orig plag ans
    """
    method = "simhash"
    if argv and argv[0] == "--method":
        if len(argv) < 2:
            raise InvalidArgumentError("--method 需要指定算法（simhash 或 cosine）")
        method = argv[1].lower()
        if method not in _METHODS:
            raise InvalidArgumentError(f"未知算法: {argv[1]}，可选 {', '.join(_METHODS)}")
        argv = argv[2:]

    if len(argv) != 3:
        raise InvalidArgumentError(
            f"参数数量错误：需要 3 个路径（原文、抄袭版、答案文件），实际 {len(argv)} 个"
        )
    return argv[0], argv[1], argv[2], method


def main(argv: list[str] | None = None) -> int:
    """端到端编排：读 → 分词 → 相似度 → 写答案。

    任意 PlagiarismError 都打印到 stderr 并返回 1，保证不向答案文件写垃圾。
    """
    if argv is None:
        argv = sys.argv[1:]

    try:
        orig_path, plag_path, ans_path, method = parse_args(argv)
        orig_tokens = tokenize(read_text(orig_path))
        plag_tokens = tokenize(read_text(plag_path))

        if not orig_tokens or not plag_tokens:
            rate = 0.0
        elif method == "cosine":
            rate = cosine_rate(orig_tokens, plag_tokens)
        else:
            h_orig = compute_simhash(orig_tokens)
            h_plag = compute_simhash(plag_tokens)
            rate = simhash_rate(h_orig, h_plag)

        write_answer(ans_path, rate)
        return 0
    except PlagiarismError as e:
        print(f"错误：{e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
