"""缩略形式模型测试。"""

import unittest

from contractions.model import (
    KINDS,
    PAIRS,
    ContractionError,
    ContractionProblem,
    all_pairs,
    check_answer,
    contract,
    expand,
    generate_problems,
)


class PairTest(unittest.TestCase):
    """逐一验证完整形式与缩略形式互转。"""


def _make_pair_test(full, short):
    def test(self):
        self.assertEqual(contract(full), short)
        self.assertEqual(expand(short).lower(), full.lower())

    test.__doc__ = "%s ↔ %s" % (full, short)
    return test


for _index, (_full, _short) in enumerate(PAIRS):
    setattr(PairTest, "test_%02d" % _index, _make_pair_test(_full, _short))


class ProblemTest(unittest.TestCase):
    """逐一验证两种题型。"""


def _make_problem_test(full, short, kind):
    def test(self):
        problem = ContractionProblem(full, short, kind)
        if kind == "contract":
            self.assertIn(full, problem.prompt)
            self.assertEqual(problem.answer, short)
        else:
            self.assertIn(short, problem.prompt)
            self.assertEqual(problem.answer, full)

    test.__doc__ = "%s 的 %s 题" % (full, kind)
    return test


for _index, (_full, _short) in enumerate(PAIRS):
    _kind = KINDS[_index % len(KINDS)]
    setattr(ProblemTest, "test_%02d" % _index, _make_problem_test(_full, _short, _kind))


class ConvertTest(unittest.TestCase):
    def test_cannot(self):
        self.assertEqual(contract("cannot"), "can't")

    def test_extra_spaces(self):
        self.assertEqual(contract("  I   am  "), "I'm")

    def test_lowercase_input(self):
        self.assertEqual(contract("i am"), "I'm")

    def test_curly_apostrophe(self):
        self.assertEqual(expand("I’m").lower(), "i am")

    def test_unknown_contract(self):
        with self.assertRaises(ContractionError):
            contract("I sleep")

    def test_unknown_expand(self):
        with self.assertRaises(ContractionError):
            expand("zzz")

    def test_empty_contract(self):
        with self.assertRaises(ContractionError):
            contract("   ")

    def test_empty_expand(self):
        with self.assertRaises(ContractionError):
            expand("")

    def test_non_string(self):
        with self.assertRaises(ContractionError):
            contract(3)  # type: ignore[arg-type]

    def test_no_duplicate_keys(self):
        texts = [full.lower() for full, _ in PAIRS]
        self.assertEqual(len(texts), len(set(texts)))

    def test_no_duplicate_shorts(self):
        texts = [short.lower() for _, short in PAIRS]
        self.assertEqual(len(texts), len(set(texts)))

    def test_pair_count(self):
        self.assertEqual(len(all_pairs()), len(PAIRS))


class ProblemValidationTest(unittest.TestCase):
    def test_bad_kind(self):
        with self.assertRaises(ContractionError):
            ContractionProblem("I am", "I'm", "guess")

    def test_unknown_full(self):
        with self.assertRaises(ContractionError):
            ContractionProblem("I sleep", "I'm", "contract")

    def test_mismatch(self):
        with self.assertRaises(ContractionError):
            ContractionProblem("I am", "I've", "contract")

    def test_frozen(self):
        problem = ContractionProblem("I am", "I'm", "contract")
        with self.assertRaises(AttributeError):
            problem.kind = "expand"  # type: ignore[misc]


class GenerateTest(unittest.TestCase):
    def test_count(self):
        self.assertEqual(len(generate_problems(10, seed=1)), 10)

    def test_unique(self):
        items = generate_problems(20, seed=2)
        keys = [(item.full, item.kind) for item in items]
        self.assertEqual(len(keys), len(set(keys)))

    def test_single_kind(self):
        items = generate_problems(8, ["expand"], seed=3)
        self.assertTrue(all(item.kind == "expand" for item in items))

    def test_seed_reproducible(self):
        self.assertEqual(generate_problems(8, seed=4), generate_problems(8, seed=4))

    def test_zero(self):
        with self.assertRaises(ContractionError):
            generate_problems(0)

    def test_bool(self):
        with self.assertRaises(ContractionError):
            generate_problems(True)

    def test_empty_kinds(self):
        with self.assertRaises(ContractionError):
            generate_problems(3, [])

    def test_bad_kind(self):
        with self.assertRaises(ContractionError):
            generate_problems(3, ["guess"])

    def test_too_many(self):
        with self.assertRaises(ContractionError):
            generate_problems(9999)


class CheckAnswerTest(unittest.TestCase):
    def test_correct(self):
        self.assertTrue(check_answer(ContractionProblem("I am", "I'm", "contract"), "I'm"))

    def test_case_insensitive(self):
        self.assertTrue(check_answer(ContractionProblem("I am", "I'm", "contract"), "i'M"))

    def test_incorrect(self):
        self.assertFalse(check_answer(ContractionProblem("I am", "I'm", "contract"), "I've"))

    def test_bad_problem(self):
        with self.assertRaises(ContractionError):
            check_answer("I am", "I'm")

    def test_bad_answer(self):
        with self.assertRaises(ContractionError):
            check_answer(ContractionProblem("I am", "I'm", "contract"), 3)


if __name__ == "__main__":
    unittest.main()
