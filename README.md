# contractions

[![CI](https://github.com/eastyou/contractions/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/contractions/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)

英语缩略形式练习：49 组常用缩写，支持完整形式与缩略形式双向查询，也能生成可打印的配对练习纸。

## 安装

```bash
pip install -e .
```

只需要 Python 3.9+，零第三方依赖。

## 用法

```bash
# 完整形式 → 缩略形式
contractions contract "I am"
# I'm

# 缩略形式 → 完整形式
contractions expand "won't"
# will not

# 查看全部对照
contractions list

# 生成 10 道混合练习，附答案
contractions sheet --count 10 --seed 1 --answers -o sheet.html

# 只练“缩略 → 完整”
contractions sheet --count 8 --kinds expand -o expand.html
```

## 功能

- 49 组常见缩略形式，含 be / have / will / would / 否定句
- 双向转换，`cannot` 与 `can't` 单独支持
- 忽略大小写、多余空格与弯引号
- 两种题型：完整 → 缩略、缩略 → 完整
- 题目去重，随机种子可复现
- A4 打印排版，答案单独一页

## 测试

```bash
python -m unittest discover -s tests -v
```

## 许可

[MIT](LICENSE) © 2026 eastyou
