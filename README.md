# LLM Lab

繁體中文的大型語言模型技術知識庫，收錄 Ollama 本地部署、RAG、AI Agent 與 KV Cache 筆記。首頁可依類別篩選或搜尋標題、摘要與內文。

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
