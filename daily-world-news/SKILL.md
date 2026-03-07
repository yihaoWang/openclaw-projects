---
name: daily-world-news
description: >
  Daily news curation with two pillars: world affairs (9 regions, multi-country perspectives)
  and tech news (RSS + GitHub + Reddit + web search with quality scoring).
  Generates combined podcast audio and delivers to Telegram.
  Use when: running daily news cron, manually generating news, creating podcast, or sending news to Telegram.
  NOT for: general web research, non-news content, or historical analysis.
---

# Daily World News + Tech Digest

Two-pillar daily news system: **時事新聞** (world affairs) + **科技新聞** (tech digest), combined into one podcast.

## Key Config
- All dates/filenames use **JST (Asia/Tokyo)**: `TZ=Asia/Tokyo date +%Y-%m-%d` → `$TODAY`
- Summaries dir: `/home/node/.openclaw/workspace/openclaw-projects/daily-world-news/summaries/`
- Skill dir: `/home/node/.openclaw/workspace/skills/daily-world-news/`

---

## PHASE 0 — Pre-flight

1. `TODAY=$(TZ=Asia/Tokyo date +%Y-%m-%d)`
2. If `summaries/${TODAY}.md` AND `summaries/${TODAY}-tech.md` both exist and were delivered → STOP

## PHASE 1 — 科技新聞 (Tech Digest)

### Step 1.1 — Read Config
- Read [TECH_SOURCES.json](TECH_SOURCES.json) for RSS, GitHub, Reddit sources
- Read [TECH_TOPICS.json](TECH_TOPICS.json) for topic definitions
- Read [TECH_FORMAT.md](TECH_FORMAT.md) for output format
- Read [SCORING.md](SCORING.md) for quality scoring rules

### Step 1.2 — Read Yesterday's Tech Summary
- Read `summaries/` for yesterday's tech file to avoid duplicates
- Stories from yesterday get -5 penalty unless major new development

### Step 1.3 — Gather Tech News (4 source layers)

**Layer A: RSS Feeds (~40 feeds)**
- For each HIGH-PRIORITY RSS feed in TECH_SOURCES.json, fetch via `web_fetch`
- Extract articles published in past 48 hours
- Tag each article with its topics from the source config
- NOTE: Not all feeds need fetching every day. Prioritize: priority=true feeds first, then sample from others
- Aim to fetch 15-20 priority feeds + 10 random non-priority feeds

**Layer B: GitHub Releases**
- For each repo in TECH_SOURCES.json `github_repos`, check via web_fetch:
  `https://github.com/{owner}/{repo}/releases.atom`
- Look for releases in past 7 days
- Tag with topics from config

**Layer C: Reddit**
- For each subreddit in TECH_SOURCES.json `reddit_subs`, fetch:
  `https://www.reddit.com/r/{sub}/hot.json?limit=10`
- Filter by min_score threshold from config
- Only include posts from past 48 hours

**Layer D: Web Search**
- Run web_search for each query in TECH_SOURCES.json `web_search_queries`
- Use freshness filter for past day
- 4 topics × 2-3 queries = 8-12 searches

### Step 1.4 — Score, Deduplicate, Rank
- Apply scoring formula from [SCORING.md](SCORING.md)
- Deduplicate: title similarity > 85% → merge, keep most authoritative
- Group by topic, sort by quality_score descending
- Minimum score threshold: 5

### Step 1.5 — Write Tech Summary
- Format per [TECH_FORMAT.md](TECH_FORMAT.md)
- Save to `summaries/${TODAY}-tech.md`
- Include: Top 3 headlines, 4 topic sections, GitHub Releases, Blog Picks, Crypto market snapshot

### Step 1.6 — Send Tech Summary to Telegram
- Use message tool: action=send, channel=telegram, target=-1003767828002, threadId=36
- message = tech summary text

---

## PHASE 2 — 時事新聞 (World Affairs)

### Step 2.1 — Read Config
- Read [FORMAT.md](FORMAT.md) for output format (STRICT)
- Read [SOURCES.md](SOURCES.md) for approved media sources

### Step 2.2 — Read Yesterday's World Summary
- Read yesterday's summary to avoid duplicates
- Only carry forward stories with significant new developments

### Step 2.3 — Gather World News
- Run 15-25 web_search queries across all 9 regions
- For major international events → Format A (multi-country perspectives from different media)
- For regional news → Format B (standard)
- Curate 15-20 stories, 3-5 using Format A
- **Every story MUST have 📎 source links** — zero tolerance

### Step 2.4 — Verify Sources
- Review all stories. Missing 📎 link → add source or remove story

### Step 2.5 — Write World Summary
- Format per [FORMAT.md](FORMAT.md)
- Save to `summaries/${TODAY}.md`

### Step 2.6 — Send World Summary to Telegram
- Use message tool: action=send, channel=telegram, target=-1003767828002, threadId=36
- message = world summary text

---

## PHASE 3 — Combined Podcast

### Step 3.1 — Read Podcast Guide
- Read [PODCAST_PROMPT.md](PODCAST_PROMPT.md) for style guide

### Step 3.2 — Write Combined Podcast Script
- **Target: 6000-10000 字** (繁體中文, ~15-25 分鐘語音)
- **⚠️ HARD MINIMUM: 4000 中文字** — 低於此字數的稿件不合格，必須重寫擴充
- **驗證方法：** 寫完後執行 `python3 -c "print(len(open('summaries/${TODAY}-podcast.md').read()))"` 確認檔案大小 **≥ 12000 bytes**（中文字約 3 bytes/字，4000字 ≈ 12000 bytes）。如不足 → 回到 Step 3.2 重寫擴充
- **注意：4000 字 ≠ 4000 bytes！** 中文字每字佔 3 bytes，不要混淆
- Structure:
  1. **開場** (~1 min) — 打招呼 + 預告今天時事和科技各 2-3 件大事
  2. **時事新聞** (~8-12 min) — 依重要性排序，5-8 個主題段落，融入多國視角
  3. **過場** — 自然轉場到科技：「聊完國際局勢，我們來看看科技圈今天有什麼動靜...」
  4. **科技新聞** (~5-8 min) — 依重要性排序，3-5 個主題段落，帶出技術觀點
  5. **市場快報** (~1 min) — 股市 + 加密貨幣重點數字
  6. **結尾** (~30 sec) — 簡短收尾
- Maintain depth and multi-country perspectives (praised — keep it up!)
- Save to `summaries/${TODAY}-podcast.md`

### Step 3.3 — Generate Audio
```bash
python3 /home/node/.openclaw/workspace/skills/daily-world-news/scripts/generate-audio.py \
  summaries/${TODAY}-podcast.md summaries/${TODAY}.mp3
```
- Verify mp3 exists after running

### Step 3.4 — Send Audio to Telegram
- Use message tool: action=send, channel=telegram, target=-1003767828002, threadId=36
- asVoice=true, filePath=summaries/${TODAY}.mp3, message="🎙️ 每日新聞 Podcast"

---

## PHASE 4 — Wrap Up

### Step 4.1 — Git Push
```bash
cd /home/node/.openclaw/workspace/openclaw-projects && git add -A && git commit -m "📰 每日新聞摘要 ${TODAY}" && git push origin main
```
- **⚠️ MUST verify push succeeded** — run `git log --oneline -1` and confirm the commit hash matches
- If push fails, retry once. If still fails, report the error.

---

## Key Rules
- All dates/filenames use **JST (Asia/Tokyo)**
- No fabricated news or URLs
- Compare perspectives by **COUNTRY**, not East/West
- No duplicates with yesterday
- Every story needs source links (📎)
- Tech news scored and ranked by quality_score
- Telegram messages: 時事 and 科技 sent **separately**, Podcast is **combined**
