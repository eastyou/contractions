"""命令行入口。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .model import (
    KINDS,
    PAIRS,
    ContractionError,
    contract,
    expand,
    generate_problems,
)
from .render import render_worksheet


def build_parser() -> argparse.ArgumentParser:
    """构造命令行解析器。"""
    parser = argparse.ArgumentParser(
        prog="contractions",
        description="英语缩略形式：转换查询与练习纸",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    short = subparsers.add_parser("contract", help="完整形式转缩略形式")
    short.add_argument("phrase", help="如 \"I am\"")

    full = subparsers.add_parser("expand", help="缩略形式转完整形式")
    full.add_argument("short", help="如 \"I'm\"")

    subparsers.add_parser("list", help="列出全部对照")

    sheet = subparsers.add_parser("sheet", help="生成 A4 练习纸")
    sheet.add_argument("--count", type=int, default=8, help="题目数量，默认 8")
    sheet.add_argument("--kinds", default=",".join(KINDS), help="题型，逗号分隔：contract、expand")
    sheet.add_argument("--seed", type=int, default=None, help="随机种子")
    sheet.add_argument("--title", default="缩略形式练习", help="练习纸标题")
    sheet.add_argument("--answers", action="store_true", help="追加参考答案")
    sheet.add_argument("-o", "--output", default=None, help="输出文件")
    return parser


def _write_output(text: str, output: Optional[str]) -> None:
    if not output:
        print(text)
        return
    path = Path(output)
    if path.parent and str(path.parent) not in ("", "."):
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print("已写入 %s" % path)


def _parse_kinds(text: str) -> List[str]:
    parts = [part.strip() for part in text.split(",") if part.strip()]
    if not parts:
        raise ContractionError("至少需要一种题型")
    return parts


def main(argv: Optional[List[str]] = None) -> int:
    """命令行主函数，返回进程退出码。"""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "contract":
            print(contract(args.phrase))
            return 0
        if args.command == "expand":
            print(expand(args.short))
            return 0
        if args.command == "list":
            for full, short in PAIRS:
                print("%-12s %s" % (full, short))
            return 0
        problems = generate_problems(args.count, _parse_kinds(args.kinds), args.seed)
        _write_output(render_worksheet(problems, args.title, args.answers), args.output)
        return 0
    except ContractionError as exc:
        print("错误：%s" % exc, file=sys.stderr)
        return 2
    except OSError as exc:
        print("写入失败：%s" % exc, file=sys.stderr)
        return 1
