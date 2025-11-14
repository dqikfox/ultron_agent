# ULTRON Avatar Game - Quick Test Card
## v3.0.6 - Maverick Improvements

**⏱️ 5-Minute Test** | **🎯 3 New Features** | **✅ Ready to Test**

---

## 🚀 Quick Start

```bash
# 1. Start the game
start_avatar_game.bat

# 2. Open browser
http://localhost:8082

# 3. Spawn avatar
Press SPACE key
```

---

## 🧪 Test 1: Emotion Particles (30 seconds)

```
✅ Enable "Enhanced Animations" checkbox
✅ Spawn avatar (SPACE)
✅ Type: "This is amazing!"
   → See 🟢 GREEN particles (15)
✅ Type: "This is terrible"
   → See 🔴 RED particles (8)
✅ Type: "What time is it?"
   → See 🔵 BLUE particles (5)
```

**Expected**: Particles change color and count based on emotion

---

## 🧪 Test 2: Memory System (1 minute)

```
✅ Send 5 messages to avatar
✅ Click on avatar
✅ Look for "RELATIONSHIP" section
   → Score: Should be positive/negative
   → Messages: Should show 5
   → Recent Mood: Should show last sentiment
```

**Expected**: Character card shows relationship stats

---

## 🧪 Test 3: Multi-Avatar Memory (2 minutes)

```
✅ Spawn 3 different avatars
✅ Chat with each separately
✅ Click each avatar
   → Each has independent memory
   → Each has unique relationship score
```

**Expected**: Each avatar tracks its own conversations

---

## 📊 Quick Results

| Feature | Working? | Notes |
|---------|----------|-------|
| Emotion Particles | ☐ Yes ☐ No | Color: _____ |
| Memory System | ☐ Yes ☐ No | Score: _____ |
| Character Cards | ☐ Yes ☐ No | Messages: ___ |

---

## 🐛 Common Issues

**Particles not showing?**
→ Enable "Enhanced Animations" checkbox

**No sentiment detected?**
→ AWS not configured (optional feature)

**Server not running?**
→ Run `start_avatar_game.bat`

---

## 🎯 Success Criteria

✅ Particles change color (4 colors)  
✅ Relationship score updates  
✅ Memory tracks conversations  
✅ Character cards enhanced  

**All working?** → ✅ TEST PASSED

---

## 📝 Quick Feedback

**What worked well?**
_________________________________

**What needs improvement?**
_________________________________

**Suggestions?**
_________________________________

---

## 📚 Full Documentation

- `MAVERICK_IMPROVEMENTS.md` - Expert recommendations
- `IMPROVEMENTS_TEST_GUIDE.md` - Detailed testing
- `IMPLEMENTATION_REPORT.md` - Technical details

---

**⏱️ Total Test Time**: 5 minutes  
**🎯 Features Tested**: 3  
**✅ Ready**: YES
