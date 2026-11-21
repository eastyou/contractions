"""缩略形式渲染测试。"""

import html
import unittest

from contractions.model import (
    ContractionError,
    ContractionProblem,
    generate_problems,
)
from contractions.render import render_worksheet


class WorksheetTest(unittest.TestCase):
    def setUp(self):
        self.items = generate_problems(6, seed=11)

    def test_skeleton(self):
        page = render_worksheet(self.items)
        self.assertIn("<!DOCTYPE html>", page)
        self.assertTrue(page.rstrip().endswith("</html>"))

    def test_cards(self):
        page = render_worksheet(self.items)
        self.assertEqual(page.count('class="card"'), 6)

    def test_tags(self):
        page = render_worksheet(self.items)
        self.assertIn("完整 → 缩略", page)
        self.assertIn("缩略 → 完整", page)

    def test_no_answers(self):
        self.assertNotIn("参考答案", render_worksheet(self.items))

    def test_answers(self):
        page = render_worksheet(self.items, answers=True)
        self.assertIn("参考答案", page)
        self.assertEqual(page.count("<tr>"), 7)

    def test_answer_values(self):
        page = html.unescape(render_worksheet(self.items, answers=True))
        for item in self.items:
            self.assertIn(item.answer, page)

    def test_custom_title(self):
        page = render_worksheet(self.items, title="二班缩略")
        self.assertIn("二班缩略", page)

    def test_empty(self):
        with self.assertRaises(ContractionError):
            render_worksheet([])

    def test_bad_item(self):
        with self.assertRaises(ContractionError):
            render_worksheet(["I am"])

    def test_prompts(self):
        page = html.unescape(render_worksheet(self.items))
        for item in self.items:
            self.assertIn(item.prompt, page)

    def test_escaping(self):
        page = render_worksheet(self.items, title="A&B")
        self.assertIn("A&amp;B", page)

    def test_apostrophe(self):
        page = render_worksheet(
            [ContractionProblem("I am", "I'm", "contract")], answers=True
        )
        self.assertIn("I&#x27;m", page)


if __name__ == "__main__":
    unittest.main()
