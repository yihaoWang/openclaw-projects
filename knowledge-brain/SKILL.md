---
name: knowledge-brain
description: >
  Daily knowledge consolidation and second-brain management. Use when:
  (1) Running the daily knowledge consolidation cron job,
  (2) User asks to organize, review, or search their knowledge base,
  (3) User says "記下這個" or "remember this insight",
  (4) Manually triggered knowledge extraction from conversations or content.
  Manages the knowledge/ directory structure with dated markdown files,
  INDEX.md cross-references, and LanceDB atomic storage.
---

# Knowledge Brain

A personal knowledge management system that consolidates insights from all conversations,
video summaries, articles, and decisions into a structured, searchable knowledge base.

## Architecture

```
knowledge/
├── INDEX.md          # Master index, sorted by date (newest first)
├── investing/        # Investment theories, market views, strategies
├── tech/             # Technical knowledge, tools, architecture
├── decisions/        # Important decisions with reasoning
└── misc/             # Everything else worth keeping
```

## Knowledge File Format

Each file: `knowledge/<category>/YYYY-MM-DD-<slug>.md`

```markdown
# <Title>

**日期：** YYYY-MM-DD
**來源：** <source — video title, conversation, article URL, etc.>
**標籤：** #tag1 #tag2 #tag3

## 核心觀點
- Bullet points of key insights

## 關鍵數據
- Numbers, stats, evidence (if any)

## 延伸思考
- Connections to other knowledge, implications, open questions

## 相關條目
- [[YYYY-MM-DD-other-slug]] (manual cross-references when relevant)
```

## Daily Consolidation Workflow

Run nightly (JST 23:00 via cron) or manually triggered:

1. Determine today's date: `TZ=Asia/Tokyo date +%Y-%m-%d`
2. Read `memory/<today>.md` for conversation logs
3. Read `knowledge/INDEX.md` to understand existing knowledge
4. Extract valuable insights — skip if nothing worth recording
5. For each insight:
   a. Write `knowledge/<category>/<today>-<slug>.md` using the format above
   b. Store atomic version in LanceDB via `memory_store` (< 500 chars each)
      - Use category `fact` for knowledge, `decision` for decisions
      - Include source and date in the stored text for retrieval
6. Update `knowledge/INDEX.md` — add new entries under the correct section, newest first

## INDEX.md Format

```markdown
# Knowledge Index

## 📈 Investing
- [2026-03-12 Thiel 壟斷理論](investing/2026-03-12-thiel-monopoly-theory.md) — 零競爭=超額利潤
- [2026-03-10 ...](investing/2026-03-10-xxx.md) — one-line summary

## 💻 Tech
...

## 🎯 Decisions
...

## 📝 Misc
...
```

## Quality Rules

- **Don't force it** — if nothing is worth recording, produce nothing
- **Atomic LanceDB entries** — each insight stored separately, < 500 chars, with keywords
- **Dated filenames** — always prefix with YYYY-MM-DD for browsability
- **One insight per file** — unless tightly related points from same source
- **Cross-reference** — note connections to existing knowledge when obvious
- **Slug in English** — for filesystem compatibility; content can be in any language

## Manual Capture

When user says "記下這個" or similar during conversation:
1. Extract the insight from current context
2. Write to appropriate `knowledge/<category>/<today>-<slug>.md`
3. Update INDEX.md
4. Store in LanceDB
5. Confirm to user what was captured

## Searching Knowledge

When user asks about past knowledge:
1. First try `memory_recall` with relevant keywords
2. If needed, grep through `knowledge/` files
3. Check INDEX.md for topic browsing
4. Synthesize findings from multiple entries when relevant
