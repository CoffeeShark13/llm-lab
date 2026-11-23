"""Regression checks for provenance, retrieval and stale-data detection."""

import copy
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import learning
import wiki
from build import ROOT, load_articles


class WikiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = wiki.lint()
        cls.articles = load_articles()
        cls.lesson = learning.load_lesson(cls.index, cls.articles)

    def test_five_substantive_sources_with_provenance(self):
        self.assertGreaterEqual(len(self.index["sources"]), 5)
        for source in self.index["sources"]:
            passages = [p for p in self.index["passages"] if p["source"] == source["id"]]
            self.assertGreaterEqual(len(passages), 2)
            self.assertGreater(sum(len(p["text"]) for p in passages), 150)
            self.assertTrue(source["url"].startswith("https://"))

    def test_chinese_query_returns_cited_indexing_passage(self):
        results = wiki.retrieve(self.index, "切分 索引 metadata Node embeddings")
        self.assertEqual(results[0]["id"], "S03-2")
        self.assertIn("S05-1", [r["id"] for r in results])

    def test_normalization_and_empty_query(self):
        self.assertEqual(wiki.retrieve(self.index, "ＮＯＤＥ"), wiki.retrieve(self.index, "node"))
        self.assertEqual(wiki.retrieve(self.index, " "), [])

    def test_unrelated_query_has_no_support(self):
        self.assertEqual(wiki.retrieve(self.index, "量子糾纏"), [])

    def test_query_records_can_be_reproduced(self):
        digest = hashlib.sha256((ROOT / ".wiki/index.json").read_bytes()).hexdigest()
        records = list((ROOT / ".wiki/queries").glob("0[1-4]-*.json"))
        self.assertEqual(len(records), 4)
        for path in records:
            record = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(record["index_sha256"], digest)
            self.assertEqual(record["results"], wiki.retrieve(self.index, record["question"]))

    def test_unsupported_lesson_reference_is_rejected(self):
        broken = copy.deepcopy(self.lesson)
        broken["slides"][0]["evidence"] = ["S99-1"]
        with patch.object(learning.json, "loads", return_value=broken):
            with self.assertRaisesRegex(ValueError, "證據段落不存在"):
                learning.load_lesson(self.index, self.articles)

    def test_source_evidence_mismatch_is_rejected(self):
        broken = copy.deepcopy(self.lesson)
        broken["slides"][0]["sources"] = ["S05"]
        with patch.object(learning.json, "loads", return_value=broken):
            with self.assertRaisesRegex(ValueError, "來源與證據不一致"):
                learning.load_lesson(self.index, self.articles)

    def test_changed_input_and_article_are_detected(self):
        with tempfile.TemporaryDirectory(prefix="llm-wiki-test-") as directory:
            root = Path(directory)
            shutil.copytree(ROOT / ".wiki/raw", root / ".wiki/raw")
            shutil.copyfile(ROOT / ".wiki/sources.json", root / ".wiki/sources.json")
            with patch.object(wiki, "ROOT", root), patch.object(wiki, "WIKI", root / ".wiki"):
                _, outputs = wiki.source_data()
                for name, value in outputs.items():
                    path = root / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(value.encode("utf-8"))
                wiki.lint()
                raw = next((root / ".wiki/raw").glob("*.json"))
                original = raw.read_bytes()
                raw.write_bytes(original + b"\n")
                with self.assertRaisesRegex(ValueError, "已過期"):
                    wiki.lint()
                raw.write_bytes(original)
                article = next((root / "content").glob("*.json"))
                article.write_bytes(b"{}\n")
                with self.assertRaisesRegex(ValueError, "已過期"):
                    wiki.lint()


if __name__ == "__main__":
    unittest.main(verbosity=2)
