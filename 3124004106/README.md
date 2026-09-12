# 论文查重（个人项目1）

广东工业大学软件工程 个人项目1。给定原文文件与抄袭版文件，输出重复率到答案文件。

## 用法

```bash
python 3124004106/main.py [原文文件] [抄袭版文件] [答案文件]
```

扩展算法：

```bash
python 3124004106/main.py --method cosine [原文文件] [抄袭版文件] [答案文件]
```

默认算法为 `simhash`，可选 `cosine`。

## 输出

答案文件写入两位小数浮点数，例如 `0.69`。

## 模块结构

```
3124004106/
├── main.py            # 命令行入口、参数解析、端到端编排
├── simhash.py         # SimHash 指纹、Hamming 距离、余弦相似度
├── tokenizer.py       # jieba 分词 + 标点/空白过滤
├── fileio.py          # 文件读写（UTF-8 优先、GBK 回退）
├── exceptions.py      # PlagiarismError 异常层级
├── profile_simhash.py # cProfile 性能分析脚本
├── pyproject.toml     # ruff 配置
├── requirements.txt
└── tests/
    ├── conftest.py
    ├── test_simhash.py
    ├── test_tokenizer.py
    ├── test_fileio.py
    ├── test_exceptions.py
    ├── test_main.py
    └── fixtures/      # 测试样例
```

## 算法

**默认：SimHash + Hamming 距离**

1. jieba 分词，过滤标点/空白
2. 对每个 token 计算 md5 稳定哈希（避免 PYTHONHASHSEED 随机化）
3. 词频加权，逐位累加 ± 权重，按符号位定 64 位指纹
4. 重复率 = 1 - hamming_distance / 64

**扩展：TF 余弦相似度**

词频向量夹角余弦，作为 SimHash 的对照。

## 异常处理

| 异常 | 场景 |
|---|---|
| `InvalidArgumentError` | 参数数量错误或 `--method` 值非法 |
| `FileReadError` | 文件不存在/无权限/编码无法识别 |
| `EmptyFileError` | 文件内容为空（或仅空白） |
| `FileWriteError` | 答案文件目录不可写 |

所有异常继承 `PlagiarismError`，`main` 统一捕获后输出到 stderr 并返回退出码 1。

## 测试

```bash
cd 3124004106
python -m pytest tests/ --cov=. --cov-report=term-missing --cov-branch
```

75 个用例，覆盖率 97%。

## 性能分析

```bash
python 3124004106/profile_simhash.py
```

10k 字合成文本耗时约 1.2s，主要瓶颈在 jieba 分词与词典加载。

## 依赖

见 `requirements.txt`：

- `jieba` 中文分词
- 开发：`pytest`、`pytest-cov`、`ruff`
