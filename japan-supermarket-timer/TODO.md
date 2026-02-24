# 📝 TODO

## ✅ Completed

### MVP (Initial Release)
- [x] Basic Telegram bot
- [x] Discount time database  
- [x] AI self-iteration workflow

### Iteration 1 (Production Ready)
- [x] Expand to 12+ supermarkets
- [x] Docker deployment
- [x] Comprehensive tests
- [x] Contributing guidelines
- [x] Better UX with emojis
- [x] New commands: /soon, /search, /nearby, /stats
- [x] Inline keyboard buttons
- [x] Regional filtering
- [x] Item categorization
- [x] Multi-language infrastructure

### Iteration 2 (Smart Notifications)
- [x] Reminder system implementation
- [x] /remind command with customizable timing
- [x] User preference storage
- [x] Background notification loop
- [x] /remind_off to disable
- [x] /remind_status to check settings

### Iteration 3 (Favorite Stores)
- [x] /favorite add command
- [x] /favorite remove command
- [x] /favorite list command
- [x] Filter reminders by favorites
- [x] Fuzzy store name matching
- [x] Backwards compatibility with old data

## 🚧 In Progress

- [ ] Test reminder + favorites system with real users
- [ ] Fix any async issues in reminder loop
- [ ] Add more specific store locations (Tokyo area priority)

## 📋 Next Iteration (Phase 3)

### High Priority
- [ ] **User favorite stores** - Let users subscribe to specific chains
  - Modify reminder system to filter by favorites
  - /favorite add <store>
  - /favorite remove <store>
  - /favorite list

- [ ] **Location-based search** (GPS)
  - Integration with Google Maps API
  - /near command with distance calculation
  - Show nearest stores with active/upcoming discounts

- [ ] **Better data collection**
  - Add 20+ more specific Tokyo locations
  - Kansai region expansion (Osaka, Kyoto, Kobe)
  - Weekend vs weekday schedules
  - Holiday schedules

### Medium Priority
- [ ] **Price tracking** (if feasible)
  - Track actual discount prices
  - Price trends over time
  - Best value alerts

- [ ] **Web interface**
  - Simple web app to browse schedules
  - Map view of stores
  - Share functionality

- [ ] **Community features**
  - User-submitted store times
  - Verification system
  - Report changes

### Low Priority  
- [ ] **Full Japanese localization**
  - All messages in Japanese option
  - /lang command to switch

- [ ] **LINE bot**
  - Port to LINE messaging platform
  - Popular in Japan

- [ ] **Analytics**
  - Track popular stores
  - Peak usage times
  - Popular commands

## 🐛 Known Issues

- [ ] Reminder loop needs testing with multiple users
- [ ] Long message splitting could be improved
- [ ] Time zone handling (currently assumes JST)
- [ ] No rate limiting on commands

## 💡 Ideas for AI to Implement

When you (AI) run the next iteration, prioritize these:

1. **Favorite Stores Feature** - Most requested, high impact
   - Files to modify: bot/reminders.py, bot/telegram_bot.py
   - Add /favorite commands
   - Filter reminders by favorites

2. **More Tokyo Locations** - Data expansion
   - Add 10-20 specific stores with addresses
   - Focus on Shibuya, Shinjuku, Shinagawa areas
   - Include coordinates for future GPS feature

3. **Weekend Schedule Variations** - Better accuracy
   - Many stores have different weekend times
   - Add weekday/weekend schedule support
   - Update data structure

4. **Better Error Handling** - Code quality
   - Add try/catch around all API calls
   - User-friendly error messages
   - Logging system

5. **Performance Optimization** - Scale preparation
   - Cache frequently accessed data
   - Optimize time calculations
   - Database indexing for faster searches

## 🎯 Success Metrics

Track these to measure impact:

- [ ] Active users (target: 100+)
- [ ] Daily active users (target: 20+)
- [ ] Reminder subscriptions (target: 50+)
- [ ] Store coverage (target: 50+ stores)
- [ ] User satisfaction (gather feedback)

## 📖 Documentation Needs

- [ ] Video tutorial (Japanese)
- [ ] Blog post about the project
- [ ] Screenshots for README
- [ ] FAQ section
- [ ] Privacy policy (for user data)

---

**AI Notes:**
- Each iteration should add 1-2 major features
- Focus on user value over code complexity
- Test thoroughly before committing
- Update this TODO after each iteration
- Document decisions in commit messages

**Current Priority:** Favorite stores + More Tokyo locations
