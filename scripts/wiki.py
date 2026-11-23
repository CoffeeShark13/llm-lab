"""Ingest reviewed source notes and retrieve cited passages without dependencies."""

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from datetime import datetime, timezone

from build import ROOT, validate

WIKI = ROOT / ".wiki"


def dump(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def source_data():
    manifest = json.loads((WIKI / "sources.json").read_text(encoding="utf-8"))
    sources, passages, outputs = [], [], {}
    seen_ids, seen_files = set(), set()
    for source in manifest["sources"]:
        source_id, filename = source["id"], source["file"]
        if not re.fullmatch(r"S\d{2}", source_id) or source_id in seen_ids:
            raise ValueError("來源編號無效或重複")
        if filename in seen_files or not re.fullmatch(r"[a-z0-9-]+\.json", filename):
            raise ValueError("來源檔名無效或重複")
        seen_ids.add(source_id)
        seen_files.add(filename)
        raw = (WIKI / "raw" / filename).read_bytes()
        article = json.loads(raw)
        validate(article, filename)
        outputs[f"content/{filename}"] = dump(article)
        sources.append({"id": source_id, "slug": article["slug"], "title": article["title"],
                        "url": article["references"][0]["url"],
                        "sha256": hashlib.sha256(raw).hexdigest()})
        for number, section in enumerate(article["sections"], 1):
            passages.append({"id": f"{source_id}-{number}", "source": source_id,
                             "slug": article["slug"], "heading": section["heading"],
                             "text": "\n".join(section["paragraphs"]),
                             "anchor": f"section-{number}"})
    if len(sources) < 5:
        raise ValueError("至少需要五份實質來源筆記")
    index = {"reviewed_on": manifest["reviewed_on"], "scope": manifest["scope"],
             "sources": sources, "passages": passages}
    outputs[".wiki/index.json"] = dump(index)
    return index, outputs


def tokens(query):
    text = unicodedata.normalize("NFKC", query).lower()
    terms = re.findall(r"[a-z0-9]+", text)
    for run in re.findall(r"[\u3400-\u9fff]+", text):
        terms.extend(run[i:i + 2] for i in range(max(1, len(run) - 1)))
    return set(terms)


def retrieve(index, question, limit=6):
    terms = tokens(question)
    results = []
    for passage in index["passages"]:
        haystack = unicodedata.normalize("NFKC", passage["heading"] + " " + passage["text"]).lower()
        matches = sorted(term for term in terms if term in haystack)
        if matches:
            results.append({**passage, "score": len(matches), "matched": matches})
    results.sort(key=lambda row: (-row["score"], row["id"]))
    return results[:limit]


def lint():
    index, outputs = source_data()
    for name, expected in outputs.items():
        path = ROOT / name
        if not path.is_file() or path.read_bytes() != expected.encode("utf-8"):
            raise ValueError(f"{name} 已過期，請執行 python scripts/wiki.py ingest")
    return index


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["ingest", "query", "status", "lint"])
    parser.add_argument("question", nargs="?")
    parser.add_argument("--limit", type=int, default=6)
    parser.add_argument("--output", help="將查詢證據存到專案內的 JSON 檔案")
    args = parser.parse_args()
    try:
        if args.command == "ingest":
            index, outputs = source_data()
            for name, value in outputs.items():
                path = ROOT / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(value.encode("utf-8"))
        else:
            index = lint()
        if args.command == "query":
            if not args.question or not args.question.strip() or not 1 <= args.limit <= 100:
                parser.error("query 需要非空問題，limit 必須介於 1 和 100")
            results = retrieve(index, args.question, args.limit)
            evidence = {"executed_at": datetime.now(timezone.utc).isoformat(),
                        "question": args.question, "method": "keyword-bigram-overlap",
                        "index_sha256": hashlib.sha256((WIKI / "index.json").read_bytes()).hexdigest(),
                        "results": results, "gap": "" if results else "找不到支持段落，請改寫查詢或補入資料。"}
            if args.output:
                path = (ROOT / args.output).resolve()
                if not path.is_relative_to(WIKI / "queries") or path.suffix != ".json":
                    parser.error("output 只能寫入 .wiki/queries/ 內的 JSON")
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(dump(evidence).encode("utf-8"))
            print(dump(evidence))
        else:
            print(f"{args.command}: {len(index['sources'])} sources, {len(index['passages'])} passages.")
    except (ValueError, OSError, KeyError, TypeError) as error:
        raise SystemExit(str(error))


if __name__ == "__main__":
    main()
