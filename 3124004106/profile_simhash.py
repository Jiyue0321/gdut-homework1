"""cProfile 性能分析：合成 10k 字文本跑 SimHash，输出热点函数与图表。

用法：
    python profile_simhash.py
"""

from __future__ import annotations

import cProfile
import io
import pstats
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from simhash import compute_simhash, simhash_rate  # noqa: E402
from tokenizer import tokenize  # noqa: E402


def _synth_text(words: list[str], n: int, seed: int = 42) -> str:
    rng = random.Random(seed)
    return "，".join(rng.choice(words) for _ in range(n))


def _build_corpus() -> list[str]:
    """从作业样例扩展出一个 ~50 词的小词表，便于压测。"""
    base = (
        "今天 星期天 周天 天气 晴 朗 晚上 我 要 去 看 电影 "
        "学校 课程 论文 算法 查重 相似度 文本 分析 计算 "
        "星期一 星期二 星期三 时间 学期 学号 学生 老师 课堂 "
        "作业 项目 代码 测试 单元 覆盖率 性能 内存 函数 模块"
    )
    return base.split()


def run_simhash(n: int = 10000) -> float:
    words = _build_corpus()
    text_a = _synth_text(words, n, seed=1)
    text_b = _synth_text(words, n, seed=2)
    ta = tokenize(text_a)
    tb = tokenize(text_b)
    ha = compute_simhash(ta)
    hb = compute_simhash(tb)
    return simhash_rate(ha, hb)


_FUNC_LABELS = {
    "run_simhash": "run_simhash（端到端跑一次查重）",
    "tokenize": "tokenize（jieba 分词 + 去标点）",
    "lcut": "jieba.lcut（分词入口）",
    "cut": "jieba.cut（分词主循环）",
    "__cut_DAG": "jieba.__cut_DAG（基于 DAG 切词）",
    "get_DAG": "jieba.get_DAG（构建有向无环图）",
    "check_initialized": "jieba.check_initialized（懒加载词典）",
    "initialize": "jieba.initialize（加载默认词典）",
    "calc": "jieba.calc（Viterbi 求最大概率路径）",
    "_is_punctuation": "_is_punctuation（标点过滤）",
    "_synth_text": "_synth_text（合成测试文本）",
    "_stable_hash": "_stable_hash（md5 稳定哈希）",
    "compute_simhash": "compute_simhash（计算 64 位指纹）",
    "simhash_rate": "simhash_rate（Hamming 归一化）",
}


def _label(short: str) -> str:
    """给函数名加中文说明，便于博客读者理解。"""
    for key, label in _FUNC_LABELS.items():
        if key in short:
            return label
    return short


def _top_functions(stats: pstats.Stats, n: int = 10) -> list[tuple[str, float]]:
    """返回 (函数名, 累计耗时秒) 前 n。"""
    rows: list[tuple[str, float]] = []
    for func, (_, _, _, cumtime, _) in stats.stats.items():
        filename, lineno, name = func
        short = f"{Path(filename).name}:{lineno}({name})"
        rows.append((_label(short), cumtime))
    rows.sort(key=lambda x: x[1], reverse=True)
    return rows[:n]


def _plot(top: list[tuple[str, float]], out: Path) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")  # 无窗口环境也能保存
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib 未安装，跳过绘图")
        return

    # 中文字体：Windows 上 SimHei 通常可用
    plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "Arial Unicode MS"]
    plt.rcParams["axes.unicode_minus"] = False

    names = [t[0] for t in top][::-1]
    times = [t[1] for t in top][::-1]
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.barh(names, times, color="#4a7cff")
    ax.set_xlabel("累计耗时 (秒)")
    ax.set_title("SimHash 10k 字性能分析 (cProfile)")
    for i, v in enumerate(times):
        ax.text(v + 0.01, i, f"{v:.3f}s", va="center")
    fig.tight_layout()
    fig.savefig(out, dpi=120)
    print(f"性能图已写入：{out}")


def main() -> int:
    profile = cProfile.Profile()
    profile.enable()
    rate = run_simhash(n=10000)
    profile.disable()

    buf = io.StringIO()
    stats = pstats.Stats(profile, stream=buf).sort_stats("cumulative")
    stats.print_stats(15)
    print(f"10k 字合成文本 SimHash 重复率：{rate:.4f}")
    print(buf.getvalue())

    out_prof = Path(__file__).resolve().parent / "profile.out"
    stats.dump_stats(str(out_prof))
    print(f"性能数据已写入：{out_prof}")

    top = _top_functions(stats, n=10)
    _plot(top, Path(__file__).resolve().parent / "profile.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
