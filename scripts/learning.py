"""Render the source-linked Wiki, workflow and HTML lesson from JSON."""

import json
from html import escape as h

from build import ROOT, layout, required_list, required_text
from wiki import lint


def load_lesson(index, articles):
    lesson = json.loads((ROOT / ".wiki/lesson.json").read_text(encoding="utf-8"))
    required_text(lesson, "title")
    required_text(lesson, "subtitle")
    required_text(lesson, "audience")
    slides = required_list(lesson, "slides", 8, dict)
    if len(slides) > 10:
        raise ValueError("簡報需為 8–10 頁")
    ids = set()
    sources = {s["id"] for s in index["sources"]}
    passages = {p["id"]: p for p in index["passages"]}
    slugs = {a["slug"] for a in articles}
    kinds = {"cover", "compare", "flow", "example", "checks", "workflow", "references"}
    for slide in slides:
        identity = required_text(slide, "id")
        if identity in ids or not identity.isascii() or not identity.replace("-", "").isalnum():
            raise ValueError("投影片 id 重複或無效")
        ids.add(identity)
        if slide.get("kind") not in kinds:
            raise ValueError("投影片版型無效")
        required_text(slide, "title")
        required_text(slide, "lead")
        for item in required_list(slide, "items", item_type=dict):
            required_text(item, "label")
            required_text(item, "text")
        if not set(required_list(slide, "sources")) <= sources:
            raise ValueError(f"{identity}: 來源不存在")
        evidence = required_list(slide, "evidence")
        if not set(evidence) <= set(passages):
            raise ValueError(f"{identity}: 證據段落不存在")
        if {passages[p]["source"] for p in evidence} != set(slide["sources"]):
            raise ValueError(f"{identity}: 來源與證據不一致")
        if not set(required_list(slide, "wiki")) <= slugs:
            raise ValueError(f"{identity}: Wiki 頁面不存在")
    return lesson


def learning_layout(title, description, body, script=""):
    html = layout(title + "｜LLM Lab", description, body, base="../", script=script)
    return html.replace('</head>', '  <link rel="stylesheet" href="../assets/learning.css">\n</head>')


def item_list(items, class_name="lesson-items"):
    return f'<ol class="{class_name}">' + "".join(
        f'<li><h3>{h(item["label"])}</h3><p>{h(item["text"])}</p></li>' for item in items
    ) + '</ol>'


def source_links(slide, index):
    sources = {s["id"]: s for s in index["sources"]}
    passages = {p["id"]: p for p in index["passages"]}
    evidence = " · ".join(
        f'<a href="../pages/{h(passages[p]["slug"])}.html#{h(passages[p]["anchor"])}">{h(p)}</a>'
        for p in slide["evidence"]
    )
    labels = {s["slug"]: s["title"] for s in index["sources"]}
    labels.update({"rag-indexing-wiki": "從文件到可引用的片段", "rag-evaluation-wiki": "生成前的證據檢查"})
    wiki = " · ".join(f'<a href="../pages/{h(slug)}.html">{h(labels[slug])}</a>'
                      for slug in slide["wiki"])
    original = " · ".join(f'<a href="{h(sources[s]["url"])}">{h(s)}</a>' for s in slide["sources"])
    return f'<footer class="slide-sources"><p>Wiki：{wiki}</p><p>證據：{evidence}　原始來源：{original}</p></footer>'


def render_slides(lesson, index):
    slides = []
    for number, slide in enumerate(lesson["slides"], 1):
        heading = "h1" if number == 1 else "h2"
        contents = item_list(slide["items"])
        if slide["kind"] == "references":
            contents += '<ul class="reference-list">' + "".join(
                f'<li><span>{h(s["id"])}</span><a href="{h(s["url"])}">{h(s["title"].split("｜", 1)[1])}</a></li>'
                for s in index["sources"]
            ) + '</ul>'
        slides.append(f'''<section class="deck-slide kind-{h(slide['kind'])}" id="{h(slide['id'])}" aria-labelledby="title-{h(slide['id'])}">
          <p class="slide-number">RAG 入門 / {number:02d}</p>
          <{heading} id="title-{h(slide['id'])}" tabindex="-1">{h(slide['title'])}</{heading}>
          <p class="slide-lead">{h(slide['lead'])}</p>
          {contents}{source_links(slide, index)}
        </section>''')
    body = f'''<main id="main" class="deck-wrap">
      <div class="lesson-toolbar"><a href="../wiki/index.html">RAG Wiki</a><a href="../wiki/workflow.html">流程與執行紀錄</a>
        <span>{h(lesson['audience'])}</span></div>
      <p class="deck-help">使用左右方向鍵、Home / End 或按鈕切換。可直接分享網址中的頁面錨點。列印時顯示所有投影片。</p>
      <div class="deck">{''.join(slides)}</div>
      <nav class="deck-controls" aria-label="投影片控制" hidden>
        <button type="button" id="previous">上一頁</button>
        <label for="slide-select" class="sr-only">跳至投影片</label><select id="slide-select">{''.join(f'<option value="{h(s["id"])}">{i} / {len(slides)}　{h(s["title"])}</option>' for i, s in enumerate(lesson['slides'], 1))}</select>
        <button type="button" id="next">下一頁</button>
      </nav><p id="slide-status" class="sr-only" role="status" aria-live="polite"></p>
    </main>'''
    return learning_layout(lesson["title"], lesson["subtitle"], body,
                           '<script src="../assets/slides.js" defer></script>')


def render_wiki(index, lesson):
    cards = "".join(f'''<li><span class="tag">{h(s['id'])}</span><h3><a href="../pages/{h(s['slug'])}.html">{h(s['title'].split('｜', 1)[1])}</a></h3>
        <p><a href="{h(s['url'])}">原始資料</a> · <a href="../.wiki/raw/{h(s['slug'])}.json">匯入筆記 JSON</a></p></li>'''
        for s in index["sources"])
    rows = "".join(f'''<tr><th scope="row">{i}. {h(s['title'])}</th><td>{'、'.join(h(x) for x in s['sources'])}</td>
        <td>{source_links(s, index).replace('<footer class="slide-sources">', '<div>').replace('</footer>', '</div>')}</td></tr>'''
        for i, s in enumerate(lesson["slides"], 1))
    passages = "".join(f'''<li data-passage data-text="{h(p['heading'] + ' ' + p['text'])}"><h3><a href="../pages/{h(p['slug'])}.html#{h(p['anchor'])}">{h(p['id'])} · {h(p['heading'])}</a></h3><p>{h(p['text'])}</p></li>'''
        for p in index["passages"])
    body = f'''<main id="main" class="wrap learning-page">
      <header class="learning-heading"><span class="tag">來源可追溯的檔案式 Wiki</span><h1>RAG 教學知識庫</h1>
        <p>先整理來源，再從 Wiki 查詢與製作簡報。五份來源筆記、兩篇綜合知識頁，連到十頁入門教學。</p>
        <div class="learning-actions"><a class="primary-link" href="../slides/rag-intro.html">開啟教學簡報</a><a href="workflow.html">流程與實際紀錄</a></div>
      </header>
      <section><h2>來源與閱讀範圍</h2><p>{h(index['scope'])}</p><p>查閱日期：{h(index['reviewed_on'])}。已匯入 {len(index['sources'])} 份來源、{len(index['passages'])} 個段落。原始輸入與索引雜湊保留在 <a href="../.wiki/index.json">索引 JSON</a>。</p><ul class="source-grid">{cards}</ul></section>
      <section><h2>交叉整理的知識頁</h2><ul class="topic-links">
        <li><a href="../pages/rag-indexing-wiki.html">從文件到可引用的片段</a><p>以 S02、S03、S05 對照資料準備與本機索引。</p></li>
        <li><a href="../pages/rag-evaluation-wiki.html">生成前的證據檢查</a><p>依 S02、S03 設計檢查清單，記錄實際問題。</p></li></ul></section>
      <section><h2>查詢 Wiki 段落</h2><p>關鍵字比對只提供候選證據，仍須閱讀段落確認支持程度。這裡不呼叫 LLM。</p>
        <form id="wiki-search" class="wiki-search" hidden><label for="wiki-query">問題或關鍵字</label><div><input type="search" id="wiki-query" placeholder="例如：索引 metadata 或 評估 引用"><button type="submit">搜尋段落</button></div></form>
        <p id="wiki-count" role="status">{len(index['passages'])} 個段落</p><p id="wiki-gap" hidden>找不到支持段落，請改寫查詢或補入資料。</p><ul class="passage-list">{passages}</ul></section>
      <section><h2>簡報與 Wiki 的對應</h2><p>下表也是先整理、後生成的大綱；逐頁保存原始來源與支持段落。<a href="../.wiki/lesson.json">下載大綱 JSON</a>。</p>
        <div class="table-scroll" tabindex="0" aria-label="簡報來源對照表"><table><thead><tr><th scope="col">投影片</th><th scope="col">來源</th><th scope="col">知識頁與證據</th></tr></thead><tbody>{rows}</tbody></table></div></section>
    </main>'''
    return learning_layout("RAG 教學知識庫", "五份來源、Wiki 查詢與 HTML 教學簡報", body,
                           '<script src="../assets/wiki.js" defer></script>')


def render_workflow():
    workflow = json.loads((ROOT / ".wiki/workflow.json").read_text(encoding="utf-8"))
    records = [("01-concept", "概念與流程"), ("02-indexing", "索引與切分"),
               ("03-evaluation", "評估與引用"), ("04-gap", "缺口測試")]
    evidence = []
    for name, label in records:
        record = json.loads((ROOT / f".wiki/queries/{name}.json").read_text(encoding="utf-8"))
        evidence.append(f'<li><a href="../.wiki/queries/{name}.json">{h(label)}</a>：{h(record["question"])}，命中 {len(record["results"])} 個段落。<time>{h(record["executed_at"])}</time></li>')
    sections = ''.join(f'<section><h2>{title}</h2>{item_list(workflow[key], "workflow-nodes" if key == "nodes" else "workflow-notes")}</section>'
                       for key, title in [("nodes", "工作流 Graph"), ("loops", "重複執行與回退條件"), ("observations", "本次問題與反思")])
    body = f'''<main id="main" class="wrap learning-page"><header class="learning-heading"><span class="tag">實際紀錄 · 2026-11-23</span><h1>{h(workflow['title'])}</h1><p>{h(workflow['summary'])}</p><a href="index.html">返回 RAG Wiki</a></header>
      <section><h2>先討論、後生成</h2><p>{h(workflow['discussion'])}</p></section>{sections}
      <section><h2>查詢執行結果</h2><ul class="query-records">{''.join(evidence)}</ul><p>紀錄採 UTC 時間；加八小時為台北時間。這些 JSON 保存查詢時的段落全文與索引 SHA-256。</p></section>
      <section><h2>驗證與繳交</h2><p>建置、檢查與瀏覽驗證的實際結果見 <a href="../workflow-log.md">執行紀錄</a>。<a href="../submission.md">繳交文字草稿</a>保留成果位置與反思，公開網址需在發布後確認。</p></section>
      <section><h2>目前的實作範圍</h2><p>{h(workflow['limitations'])}</p></section></main>'''
    return learning_layout(workflow["title"], workflow["summary"], body)


def render_learning(articles):
    index = lint()
    lesson = load_lesson(index, articles)
    return {"wiki/index.html": render_wiki(index, lesson),
            "wiki/workflow.html": render_workflow(),
            "slides/rag-intro.html": render_slides(lesson, index)}
