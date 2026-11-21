"""英语缩略形式的数据模型。"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

KINDS = ("contract", "expand")

PAIRS: Tuple[Tuple[str, str], ...] = (
    ("I am", "I'm"),
    ("I have", "I've"),
    ("I will", "I'll"),
    ("I would", "I'd"),
    ("You are", "you're"),
    ("You have", "you've"),
    ("You will", "you'll"),
    ("You would", "you'd"),
    ("He is", "he's"),
    ("He will", "he'll"),
    ("He would", "he'd"),
    ("She is", "she's"),
    ("She will", "she'll"),
    ("She would", "she'd"),
    ("It is", "it's"),
    ("It will", "it'll"),
    ("We are", "we're"),
    ("We have", "we've"),
    ("We will", "we'll"),
    ("We would", "we'd"),
    ("They are", "they're"),
    ("They have", "they've"),
    ("They will", "they'll"),
    ("They would", "they'd"),
    ("is not", "isn't"),
    ("are not", "aren't"),
    ("was not", "wasn't"),
    ("were not", "weren't"),
    ("do not", "don't"),
    ("does not", "doesn't"),
    ("did not", "didn't"),
    ("have not", "haven't"),
    ("has not", "hasn't"),
    ("had not", "hadn't"),
    ("can not", "can't"),
    ("could not", "couldn't"),
    ("will not", "won't"),
    ("would not", "wouldn't"),
    ("should not", "shouldn't"),
    ("must not", "mustn't"),
    ("let us", "let's"),
    ("that is", "that's"),
    ("what is", "what's"),
    ("who is", "who's"),
    ("there is", "there's"),
    ("here is", "here's"),
    ("how is", "how's"),
    ("where is", "where's"),
    ("when is", "when's"),
)


class ContractionError(ValueError):
    """缩略形式相关的输入错误。"""


def _norm(text: str, name: str = "内容") -> str:
    if not isinstance(text, str):
        raise ContractionError("%s必须是字符串" % name)
    value = " ".join(text.replace("’", "'").split()).lower()
    if not value:
        raise ContractionError("%s不能为空" % name)
    return value


def _build_maps() -> Tuple[Dict[str, str], Dict[str, str]]:
    forward: Dict[str, str] = {}
    backward: Dict[str, str] = {}
    for full, short in PAIRS:
        forward[_norm(full)] = short
        backward.setdefault(_norm(short), full)
    forward["cannot"] = "can't"
    return forward, backward


_FORWARD, _BACKWARD = _build_maps()


def contract(phrase: str) -> str:
    """把完整形式变成缩略形式。"""
    key = _norm(phrase, "完整形式")
    if key not in _FORWARD:
        raise ContractionError("没有对应的缩略形式：%s" % phrase)
    return _FORWARD[key]


def expand(short: str) -> str:
    """把缩略形式还原为完整形式。"""
    key = _norm(short, "缩略形式")
    if key not in _BACKWARD:
        raise ContractionError("没有对应的完整形式：%s" % short)
    return _BACKWARD[key]


@dataclass(frozen=True)
class ContractionProblem:
    """一道缩略形式题。"""

    full: str
    short: str
    kind: str

    def __post_init__(self) -> None:
        if self.kind not in KINDS:
            raise ContractionError("题型只能是 contract 或 expand")
        if _norm(self.full) not in _FORWARD:
            raise ContractionError("未知完整形式：%s" % self.full)
        if self.short != _FORWARD[_norm(self.full)]:
            raise ContractionError("完整形式与缩略形式不匹配")

    @property
    def prompt(self) -> str:
        """题干。"""
        if self.kind == "contract":
            return "%s 的缩略形式是？" % self.full
        return "%s 的完整形式是？" % self.short

    @property
    def answer(self) -> str:
        """答案。"""
        return self.short if self.kind == "contract" else self.full


def all_pairs() -> List[Tuple[str, str]]:
    """返回全部完整形式与缩略形式。"""
    return list(PAIRS)


def generate_problems(
    count: int = 8,
    kinds: Sequence[str] = KINDS,
    seed: Optional[int] = None,
) -> List[ContractionProblem]:
    """随机生成不重复的缩略形式题。"""
    if isinstance(count, bool) or not isinstance(count, int):
        raise ContractionError("题目数量必须是整数")
    if count < 1:
        raise ContractionError("题目数量至少为 1")
    chosen = list(kinds)
    if not chosen:
        raise ContractionError("至少需要一种题型")
    for kind in chosen:
        if kind not in KINDS:
            raise ContractionError("未知题型：%s" % kind)

    pool = [
        ContractionProblem(full, short, kind)
        for full, short in PAIRS
        for kind in chosen
    ]
    if count > len(pool):
        raise ContractionError("题目数量不能超过 %d" % len(pool))
    rng = random.Random(seed)
    rng.shuffle(pool)
    return pool[:count]


def check_answer(problem: ContractionProblem, answer: str) -> bool:
    """判断作答是否正确，忽略大小写与多余空格。"""
    if not isinstance(problem, ContractionProblem):
        raise ContractionError("题目必须是 ContractionProblem")
    return _norm(problem.answer) == _norm(answer, "答案")
