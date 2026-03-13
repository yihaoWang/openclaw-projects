---
name: knowledge-brain
description: >
  Knowledge management integrated with Obsidian vault + LanceDB.
  Use when: (1) User says "記下這個" or "remember this insight",
  (2) Extracting knowledge from external sources (articles, videos, news),
  (3) User asks to search or organize the knowledge base.
  No longer runs as a standalone cron — knowledge capture happens inline
  during conversations and via Bird agent's news/YT analysis.
---

# Knowledge Brain

知識管理系統，整合 Obsidian vault + LanceDB 雙層儲存。

## 儲存位置

```
/home/node/obsidian-vault/Knowledge/
├── INDEX.md          # 主索引（MOC）
├── investing/        # 投資理論、市場觀點
├── tech/             # 技術知識、架構、工具
├── decisions/        # 重要決策與推理過程
└── misc/             # 其他值得保留的知識
```

## 知識筆記格式

檔名：`<category>/YYYY-MM-DD-<slug>.md`

```markdown
# <Title>

**日期：** YYYY-MM-DD
**來源：** <來源 — 影片標題、文章 URL、對話主題等>
**標籤：** #tag1 #tag2

## 核心觀點
- Key insights (bullet points)

## 關鍵數據
- Numbers, stats, evidence

## 延伸思考
- Connections, implications, open questions

## 相關條目
- [[YYYY-MM-DD-other-slug]]
```

## 何時寫入知識庫

### ✅ 寫入（外部知識、可複用洞見）
- 從文章/影片學到的新概念或框架
- 市場分析、投資理論
- 技術架構模式、最佳實踐
- 安全漏洞、攻擊模式
- 有數據支撐的趨勢觀察

### ❌ 不寫入（放 MEMORY.md 或 Daily note）
- 個人決策記錄 → Agents/Dan/MEMORY.md
- 工程操作筆記（「我裝了 X」）→ Daily note
- 對話摘要 → Daily note
- 純記事（「明天要做 Y」）→ Daily note

## 寫入流程（雙寫）

1. 寫 Obsidian 筆記 → `/home/node/obsidian-vault/Knowledge/<category>/YYYY-MM-DD-<slug>.md`
2. 存 LanceDB → `memory_store` (< 500 chars, category: fact, importance ≥ 0.8)
   - 格式：`[知識:<category> <date>] <one-line summary>。<key detail>。來源：<source>。`
3. 更新 INDEX.md → 加入新條目，最新在上

## 搜尋知識

1. `memory_recall("query")` — 語義搜尋 LanceDB
2. `obsidian-cli search-content "keyword"` — 全文關鍵字
3. 讀 `INDEX.md` — 按主題瀏覽

## Bird Agent 整合

Bird 在推送新聞/YT 分析時，如果內容包含**可複用的知識洞見**，
應同時寫入 Knowledge vault。例如：

- YT 影片分析發現新的投資框架 → `Knowledge/investing/`
- 新聞中的技術趨勢 → `Knowledge/tech/`

這樣 Knowledge 的來源就不只是對話，還包含每日自動蒐集的外部資訊。
