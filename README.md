# LLM Lab

繁體中文的大型語言模型技術知識庫，收錄 Ollama 本地部署、RAG、AI Agent 與 KV Cache 筆記。首頁可依類別篩選或搜尋標題、摘要與內文。

新增的 [RAG Wiki](wiki/index.html) 收錄五份來源筆記、兩篇綜合知識頁、可搜尋段落，以及 [十頁 HTML 教學簡報](slides/rag-intro.html)。[流程頁](wiki/workflow.html) 與 [執行紀錄](workflow-log.md) 保存實際查詢與反思。[繳交草稿](submission.md) 供本人核對與補上發布網址。

## 重建 RAG Wiki

這是以 Codex 整理內容的檔案式 Wiki，沒有使用 Microsoft LLM Wiki 擴充功能。`.wiki/raw/` 為五份官方來源的繁體中文整理筆記，並非原文全文；`.wiki/sources.json` 保存來源清單與查閱日期。Ingest 將筆記轉為 `content/` 文章，並建立 `.wiki/index.json` 段落索引。網站文章仍只從 `content/*.json` 生成。

```sh
python scripts/wiki.py ingest
python scripts/wiki.py status
python scripts/wiki.py query "切分 索引 metadata Node embeddings"
python scripts/wiki.py lint
python scripts/build.py
python scripts/check.py
python scripts/test_wiki.py
```

`query` 使用關鍵字與中文二字組比對，輸出候選證據，沒有呼叫 LLM 或建立向量。可用 `--output .wiki/queries/example.json` 保存紀錄。Codex 讀取結果後整理知識頁與 `.wiki/lesson.json` 大綱，每頁保留 Wiki 與段落編號；程式檢查編號存在及對應，語意支持程度仍需閱讀核對。

`.wiki/lesson.json` 與 `.wiki/workflow.json` 分別是簡報與流程頁內容來源，由 `scripts/learning.py` 生成；不要手動修改 `wiki/*.html` 或 `slides/rag-intro.html`。瀏覽器簡報支援方向鍵、Home / End、按鈕、下拉選單與頁面錨點，無 JavaScript 時可線性閱讀，列印會顯示全部投影片。

## 在本機瀏覽

直接開啟 `index.html`，或在專案根目錄啟動本機伺服器，再開啟 `http://localhost:8000/`。

```sh
python -m http.server 8000
```

## 用 AI 新增文章

1. 讀取 [AGENTS.md](AGENTS.md) 與現有的 `content/*.json`，確認主題、內容格式及 slug。
2. 建立一份新 JSON。可參考 [KV Cache 範例](content/kv-cache.json)，其中包含摘要、三節內文、重點整理與官方文件。
3. 依序執行以下指令。生成器會將文章加入首頁索引，並建立獨立文章頁。檢查程式會比對來源與生成檔，也會驗證站內連結、資源和錨點。
4. 在首頁試用搜尋及分類，確認新文章可開啟並返回索引。

```sh
python scripts/build.py
python scripts/check.py
```

建置與檢查需要 Python 3.9 或以上版本，只使用標準函式庫。網站可直接由靜態主機提供。

## GitHub Pages

將專案檔案與生成的 HTML 推送到 GitHub。進入儲存庫的 **Settings → Pages**，選擇 **Deploy from a branch**，設定 `main` 與 `/(root)` 後儲存。部署完成後，Pages 會顯示網站網址。
