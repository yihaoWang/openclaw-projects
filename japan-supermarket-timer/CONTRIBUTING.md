# Contributing to Japan Supermarket Discount Timer

Thank you for your interest in contributing! This project helps people save money on quality food in Japan.

## 🎯 Ways to Contribute

### 1. Add Store Data

The most valuable contribution! If you know discount times for a supermarket:

**Steps:**
1. Fork the repository
2. Edit `data/discount_times.json`
3. Add your store following the format below
4. Test with `python tests/test_bot.py`
5. Submit a Pull Request

**Format:**
```json
{
  "name": "ストア名（日本語）",
  "name_en": "Store Name (English)",
  "chain": "Parent Company Name",
  "discount_schedule": [
    {
      "time": "19:00",
      "discount": "30%",
      "items": ["bento", "deli", "sushi"]
    },
    {
      "time": "20:30",
      "discount": "50%",
      "items": ["bento", "deli"]
    }
  ],
  "notes": "Any special information about this store or chain",
  "address": "Full address (optional, for specific locations)",
  "coordinates": {
    "lat": 35.6762,
    "lon": 139.6503
  }
}
```

**Item Categories:**
- `fresh_food` - Fresh produce, meat, fish
- `bento` - Boxed meals
- `deli` - Prepared foods (惣菜)
- `sushi` - Sushi
- `bakery` - Bread and baked goods

### 2. Report Issues

Found incorrect data or bugs?

1. Check [existing issues](https://github.com/yihaoWang/openclaw-projects/issues)
2. If not found, create a new issue
3. Include:
   - Store name and location
   - What's wrong
   - What it should be
   - When you observed it (date)

### 3. Improve Code

Want to add features or fix bugs?

**Setup Development Environment:**
```bash
# Clone the repo
git clone https://github.com/yihaoWang/openclaw-projects.git
cd openclaw-projects/japan-supermarket-timer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Run tests
python tests/test_bot.py
```

**Code Style:**
- Follow PEP 8
- Add docstrings to functions
- Write tests for new features
- Keep functions focused and small

### 4. Documentation

Help others use this project:

- Improve README.md
- Add usage examples
- Translate to other languages
- Write tutorials or blog posts

## 🔄 Pull Request Process

1. **Fork & Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write clear, focused commits
   - Follow existing code style
   - Add tests if applicable

3. **Test**
   ```bash
   python tests/test_bot.py
   ```

4. **Commit**
   ```bash
   git commit -m "feat: add XYZ store discount times"
   ```
   
   Commit message prefixes:
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation
   - `data:` - Store data updates
   - `test:` - Tests
   - `chore:` - Maintenance

5. **Push & PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a Pull Request on GitHub

## 📊 Data Quality Guidelines

When adding store data:

**✅ Good:**
- Observed personally within last month
- Specific store location with address
- Exact times you saw discounts
- Notes about variations (weekend, holidays)

**❌ Avoid:**
- Guessing or estimates
- Very old information (>6 months)
- Second-hand information without verification
- Vague times ("around 7 PM")

**Include in PR:**
- Store location (city/ward at minimum)
- When you observed the times
- Any special conditions (only weekdays, etc.)

## 🤖 AI Contributions

This project uses AI for automated improvements:

- AI creates PRs from `TODO.md`
- These PRs are marked with `[AI-Generated]`
- Please review carefully before merging
- Suggest improvements in PR comments

## 💬 Communication

- **Questions:** Open a GitHub issue with `[Question]` tag
- **Ideas:** Open a GitHub issue with `[Feature Request]` tag  
- **Urgent:** Create an issue and tag it `[Urgent]`

## 🙏 Recognition

Contributors will be:
- Listed in README.md
- Mentioned in release notes
- Credited in their PRs

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🎯 Priority Areas

Currently looking for:

1. **Store Data:**
   - Smaller regional chains
   - Specific store locations in Tokyo
   - Kansai region stores
   - 24-hour store schedules

2. **Features:**
   - Location-based search
   - Push notifications
   - User preferences
   - Web interface

3. **Translations:**
   - Full Japanese localization
   - Chinese/Korean translations

## ✨ First-Time Contributors

New to open source? Welcome!

**Easy First Issues:**
- Add a store you know
- Fix typos in documentation
- Improve error messages
- Add emojis to bot responses

Look for issues tagged `good-first-issue`.

---

**Thank you for helping make grocery shopping more affordable in Japan! 🛒💰**
