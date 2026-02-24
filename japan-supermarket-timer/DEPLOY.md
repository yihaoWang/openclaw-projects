# 🚀 部署指南

## 現狀

✅ 專案已在本地建立完成
✅ GitHub repo 已創建：https://github.com/yihaoWang/japan-supermarket-timer
❌ Token 權限不足，無法自動 push

## 手動部署步驟

### 1. 生成新的 GitHub Token（有正確權限）

去 https://github.com/settings/tokens?type=beta

選擇權限：
- Repository access: Only select repositories → japan-supermarket-timer
- Permissions:
  - ✅ Contents: Read and write
  - ✅ Pull requests: Read and write
  - ✅ Workflows: Read and write
  - ✅ Actions: Read and write

### 2. Push 代碼

```bash
cd ~/.openclaw/workspace/japan-supermarket-timer

# 設定新 token
export NEW_TOKEN="your_new_token_here"

# Push
git remote set-url origin https://x-access-token:$NEW_TOKEN@github.com/yihaoWang/japan-supermarket-timer.git
git push -u origin main
```

### 3. 設定 Secrets（for AI iteration workflow）

在 GitHub repo settings:
1. Settings → Secrets and variables → Actions
2. 新增 Repository secret:
   - Name: `ANTHROPIC_API_KEY`
   - Value: 你的 Claude API key

### 4. 啟動 Telegram Bot

```bash
# 先去 @BotFather 建立 bot，取得 token

cd ~/.openclaw/workspace/japan-supermarket-timer

# 安裝依賴
pip install -r requirements.txt

# 設定 token
export TELEGRAM_BOT_TOKEN="your_telegram_token"

# 啟動
python bot/telegram_bot.py
```

## 或者：一鍵腳本

我已經準備好一個腳本，只要：

```bash
cd ~/.openclaw/workspace/japan-supermarket-timer
./quick-deploy.sh <NEW_GITHUB_TOKEN> <TELEGRAM_TOKEN> <CLAUDE_API_KEY>
```

## AI 自我迭代觸發

Push 成功後，AI 會：
- 每 6 小時自動分析專案
- 選擇一個改進項目
- 自動建立 PR
- 你只需要 review + merge

手動觸發：
```bash
# 去 GitHub Actions tab → AI Self-Iteration → Run workflow
```

---

**專案本地位置：** `~/.openclaw/workspace/japan-supermarket-timer/`
