"""命令行行为测试。"""

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from contractions.cli import main


def run(args):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(args)
    return code, out.getvalue(), err.getvalue()


class CliTest(unittest.TestCase):
    def test_help(self):
        with self.assertRaises(SystemExit) as ctx:
            main(["--help"])
        self.assertEqual(ctx.exception.code, 0)

    def test_contract(self):
        code, out, _ = run(["contract", "I am"])
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "I'm")

    def test_contract_cannot(self):
        code, out, _ = run(["contract", "cannot"])
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "can't")

    def test_contract_unknown(self):
        code, _, err = run(["contract", "I sleep"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_expand(self):
        code, out, _ = run(["expand", "won't"])
        self.assertEqual(code, 0)
        self.assertIn("will not", out.lower())

    def test_expand_unknown(self):
        code, _, err = run(["expand", "zzz"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_list(self):
        code, out, _ = run(["list"])
        self.assertEqual(code, 0)
        self.assertEqual(len(out.strip().splitlines()), 49)
        self.assertIn("I'm", out)

    def test_sheet_stdout(self):
        code, out, _ = run(["sheet", "--count", "3", "--seed", "1"])
        self.assertEqual(code, 0)
        self.assertEqual(out.count('class="card"'), 3)

    def test_sheet_answers(self):
        code, out, _ = run(["sheet", "--count", "3", "--seed", "2", "--answers"])
        self.assertEqual(code, 0)
        self.assertIn("参考答案", out)

    def test_sheet_single_kind(self):
        code, out, _ = run(["sheet", "--count", "5", "--kinds", "expand", "--seed", "3"])
        self.assertEqual(code, 0)
        self.assertIn("缩略 → 完整", out)
        self.assertNotIn("完整 → 缩略", out)

    def test_sheet_bad_kind(self):
        code, _, err = run(["sheet", "--kinds", "guess"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_sheet_empty_kinds(self):
        code, _, err = run(["sheet", "--kinds", " , "])
        self.assertEqual(code, 2)
        self.assertIn("题型", err)

    def test_sheet_too_many(self):
        code, _, err = run(["sheet", "--count", "9999"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_sheet_to_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "sheet.html"
            code, _, _ = run(["sheet", "--count", "4", "--seed", "5", "-o", str(target)])
            self.assertEqual(code, 0)
            self.assertEqual(target.read_text(encoding="utf-8").count('class="card"'), 4)

    def test_nested_output(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "a" / "sheet.html"
            code, _, _ = run(["sheet", "--count", "1", "-o", str(target)])
            self.assertEqual(code, 0)
            self.assertTrue(target.exists())


if __name__ == "__main__":
    unittest.main()
