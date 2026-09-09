# 论文查重工具

广东工业大学软件工程课程个人项目 1 —— 中文论文查重命令行工具。

## 用法

```bash
python main.py [原文文件路径] [抄袭版文件路径] [答案文件路径]
```

示例：

```bash
python main.py orig.txt orig_add.txt ans.txt
```

`ans.txt` 输出一个浮点数（精确到小数点后 2 位），表示重复率。

## 算法

- **默认**：SimHash + Hamming 距离（64 位指纹）
- **扩展**：TF-IDF + 余弦相似度（`--method cosine` 触发）

## 环境依赖

- Python 3.10+
- 依赖见 `requirements.txt`

```bash
pip install -r requirements.txt
```

## 项目结构

```
3124004106/
├── main.py              # CLI 入口
├── simhash.py           # SimHash 与余弦相似度算法
├── tokenizer.py         # jieba 分词封装
├── fileio.py            # 文件读写与编码回退
├── exceptions.py        # 自定义异常
├── requirements.txt
├── pyproject.toml       # ruff 配置
├── profile_simhash.py   # 性能分析脚本
└── tests/               # 单元测试与 fixtures
```

## 测试

```bash
cd 3124004106
python -m pytest --cov=. --cov-report=term-missing --cov-branch
```

## 作者

苏炜康（学号 3124004106）
