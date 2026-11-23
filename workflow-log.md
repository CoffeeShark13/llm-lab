# RAG Wiki 執行紀錄

日期：2026-11-23（台北時間）。執行者：Codex，依使用者授權沿用 LLM Lab。

## 討論與範圍

讀取原作業要求與 AGENTS.md、README、四篇現有文章。先詢問課堂是否指定 Wiki 工具，使用者回覆「沒有指定，沿用專案完成」。因此採用可重跑的檔案式 Wiki，主題是 RAG 入門，不安裝框架或接上付費 API。

## 來源取得與整理

使用網頁工具閱讀 RAG 論文 arXiv v4 摘要、Microsoft RAG and indexes、LlamaIndex Introduction to RAG、Hugging Face RAG 概述與範例、LangChain RAG with Deep Agents 的索引章節。

Codex 將各來源整理為 `.wiki/raw/` 中五份繁體中文 JSON 筆記，保留閱讀範圍與原始網址。這是實質摘要輸入，不是原文全文快照。沒有聲稱下載全文 PDF 或執行官方範例。

## 實際執行

1. `python scripts/wiki.py ingest`：成功匯入 5 份來源與 15 個段落，輸出 `content/rag-source-*.json` 與 `.wiki/index.json`。
2. `python scripts/wiki.py query 'RAG 檢索 增強 生成 記憶' --output .wiki/queries/01-concept.json`：取得 6 個段落，閱讀後整理基本概念。
3. `python scripts/wiki.py query '切分 索引 metadata Node embeddings' --output .wiki/queries/02-indexing.json`：取得 6 個段落，交叉整理文件與索引。
4. `python scripts/wiki.py query '評估 引用 版本 限制' --output .wiki/queries/03-evaluation.json`：取得 6 個段落，整理評估與引用檢查。
5. `python scripts/wiki.py query '量子糾纏' --output .wiki/queries/04-gap.json`：0 個段落，工具回傳改寫查詢或補資料的缺口提示。這是刻意的負向測試。
6. Codex 讀取查詢結果後，建立兩篇綜合知識頁與 `.wiki/lesson.json` 十頁大綱。每頁保存 Wiki slug、來源編號與支持段落；再由生成器產生 HTML。

查詢 JSON 中的 `executed_at` 是實際 UTC 執行時間，`index_sha256` 可核對當時的索引。重新執行相同命令會更新時間。目前結果保存在尚未提交的 `.wiki/queries/` 檔案中；取得提交與推送授權後，才會納入 Git 版本。

## Loop 與 Graph

來源取得 → 網址與內容核對 → 筆記整理 → Ingest → Query → 大綱與證據核對 → 生成 HTML → 頁面檢查。

- 來源轉址或主題不同：回到來源取得，重新核對後匯入。
- Query 沒有支持段落：改寫查詢；仍不足則補資料，再次 Ingest。
- 大綱無法由片段支持：改寫敘述或重新 Query，再進行逐頁核對。
- 生成或瀏覽檢查失敗：修改來源 JSON、樣式或生成器，再 build、check。

## 問題與反思

觀察到 LangChain 舊 `/oss/python/langchain/rag` 網址轉到 `/oss/python/deepagents/rag`，因此改用新頁名與實際網址。將「網址、頁名與章節閱讀範圍核對」提前到 Ingest 前，避免索引混入與預期不同的內容。

第一次 query 的 Windows 終端輸出出現亂碼，JSON 檔案本身則以 UTF-8 正常保存。修正 wiki.py 的標準輸出編碼後，重新執行查詢，繁體中文已能正常顯示。

這次只有一次工作流實作，無法統計哪個節點最常出錯。可確認來源核對與輸出紀錄各有具體問題，工作流已提前加入來源檢查。資料缺口測試沒有命中，屬預期結果，沒有編造模型答錯的故事。

## 驗證結果

已完成以下實際檢查：

- `python scripts/build.py`：成功生成 15 個 HTML（首頁、11 篇文章、Wiki、流程頁、簡報）。
- `python scripts/check.py`：15 頁資料格式、生成內容一致性、站內連結、資源、錨點與單一 h1 檢查通過。這次擴充主生成器，因此 Wiki 與簡報也納入原有檢查。
- `python scripts/test_wiki.py`：8 項回歸測試通過。涵蓋五份實質來源、中文檢索、全形文字正規化、無命中查詢、四份查詢紀錄重現、無效引用攔截、來源與證據不一致攔截，以及來源或文章變動後的過期資料偵測。
- `node --check assets/slides.js` 與 `node --check assets/wiki.js`：語法檢查通過。
- 啟動 `python -m http.server 8000 --bind 127.0.0.1`，透過內建瀏覽器實際預覽。沙箱中的伺服器無法從瀏覽器連線，改用獲准的本機預覽伺服器後成功。
- 首頁搜尋「S03」得到 3 篇；再選「本地部署」得到 0 篇，清除搜尋後得到 1 篇。新文章可從首頁開啟，文章可返回索引。
- Wiki 搜尋「量子糾纏」顯示 0 段與缺口提示；搜尋「切分 索引 metadata Node embeddings」時，首項是 S03-2，與 CLI 排序一致。網頁展示全部命中，CLI 預設只回傳前 6 項。
- 簡報實測右方向鍵、Home、End、上一頁、下一頁及下拉切頁；首末頁按鈕停用狀態正確。十頁在桌面寬度逐頁檢查，寬約 1217px、高約 685px，符合 16:9；沒有橫向溢出，來源註記都位於投影片範圍內。
- Tab 鍵可到達跳至主要內容連結，焦點外框為實線。封面驗證畫面保存為 `.wiki/preview.jpg`。
- 以 390 × 844 手機視窗逐頁檢查十頁，沒有橫向溢出，來源註記保留。Wiki、流程與綜合文章頁也沒有整頁橫向溢出；對照表使用自己的橫向捲動區，程式碼區塊為 `overflow-x: auto`。測完已重設視窗尺寸。

尚未驗證：實體手機、其他瀏覽器、實際列印輸出與停用 JavaScript 的瀏覽結果。HTML 與 CSS 已提供無 JavaScript 線性閱讀及列印全部投影片的規則，這些規則尚未經實際輸出確認。未發布 GitHub Pages、未確認公開網址，也未代為繳交。
