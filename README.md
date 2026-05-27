# ⚡ NeuroFlux AI — Elite Telegram AI Revenue System

A production-ready, high-performance Telegram AI bot designed for viral growth, user engagement, and monetization.

## 🔥 Features

### AI Engines (Powered by OpenAI GPT-4.1-mini)
- **Income Score Engine** — Analyzes financial trajectory with shock-value insights
- **Decision Engine** — One authoritative decision, no hedging
- **Profile Scanner** — Resume/bio analysis with critical feedback
- **AI Chat** — Conversational AI with memory (5 free/day, unlimited for paid)
- **AI Writer** — Emails, essays, social posts, cover letters
- **Code Engine** — Write, debug, explain code in any language
- **Translator** — Any language pair
- **Summarizer** — Extract core insights from any text

### Utilities
- **Notes / To-Do** — Save and view notes
- **Habit Tracker** — Track habits with streak system
- **Finance Tracker** — Income/expense tracking with balance
- **Password Generator** — Customizable secure passwords
- **Daily Bonus** — 5 points/day engagement hook

### Growth & Monetization
- **Referral System** — Unique invite links, auto-unlock after 3 referrals
- **Lock + Viral Loop** — Full reports locked behind referral/payment wall
- **Premium Plans** — ₹99 one-time, ₹299/month, ₹999 VIP
- **Daily Alerts** — AI-generated retention notifications at 9 AM
- **Admin Panel** — User stats, broadcast system

## 🚀 Deploy on Render (1-Click)

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "NeuroFlux AI v1.0"
git remote add origin https://github.com/YOUR_USERNAME/neuroflux-ai.git
git push -u origin main
```

### Step 2: Deploy on Render
1. Go to [render.com](https://render.com)
2. Create a new Blueprint instance and connect your GitHub repository.
3. Select your `neuroflux-ai` repository
4. Add these **Environment Variables**:

| Variable | Value |
|----------|-------|
| `BOT_TOKEN` | Your Telegram bot token from @BotFather |
| `ADMIN_ID` | Your Telegram user ID |
| `OPENAI_API_KEY` | Your OpenAI API key |
| `OPENAI_BASE_URL` | `https://api.openai.com/v1` |

5. Render will automatically detect the `render.yaml` file and deploy the bot as a Background Worker.
6. The bot should go live within a few minutes.

### Step 3: Test
Send `/start` to your bot on Telegram.

## 📁 Project Structure

```
neuroflux-ai/
├── bot.py              # Main bot logic, handlers, callbacks
├── ai_engine.py        # All AI functions (OpenAI integration)
├── database.py         # SQLite database operations
├── requirements.txt    # Python dependencies
├── render.yaml         # Render Blueprint configuration
├── runtime.txt         # Python version
├── .env.example        # Environment variable template
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## 🛡️ Admin Commands

- `/admin` — View admin panel (total users, paid users, broadcast)
- `/clear` — Clear AI chat memory
- `/menu` — Show main menu
- `/profile` — View your profile

## ⚙️ Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `BOT_TOKEN` | ✅ | Telegram Bot API token |
| `ADMIN_ID` | ✅ | Your Telegram user ID for admin access |
| `OPENAI_API_KEY` | ✅ | OpenAI API key for AI features |
| `OPENAI_BASE_URL` | ✅ | OpenAI API base URL (default: https://api.openai.com/v1) |

## 💎 Monetization Structure

| Plan | Price | Features |
|------|-------|----------|
| Free | ₹0 | 5 AI messages/day, basic features |
| One-Time | ₹99 | Unlock all reports |
| Pro Monthly | ₹299/mo | Unlimited AI + premium insights |
| VIP Lifetime | ₹999 | Everything, forever |

## 📈 Growth Engine

1. User joins → Gets hooked by Income Score
2. Full report locked → Must invite 3 friends OR pay
3. Referral link shared → New users join
4. Daily alerts bring users back
5. Free limits push toward premium

## License

MIT
