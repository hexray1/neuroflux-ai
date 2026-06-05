import logging
import asyncio
import random
import string
import datetime
import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    CallbackQueryHandler, ContextTypes
)

import database as db
import ai_engine as ai

# ─── CONFIG ───────────────────────────────────────────────────
TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "5350231648"))

# ─── LOGGING ──────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("NeuroFlux")

# ─── STATES ───────────────────────────────────────────────────
(STATE_CHAT, STATE_WRITE, STATE_CODE, STATE_TRANSLATE_TEXT, STATE_TRANSLATE_LANG,
 STATE_SUMMARIZE, STATE_NOTE, STATE_HABIT_ADD, STATE_FINANCE_AMT, STATE_FINANCE_DESC,
 STATE_BROADCAST, STATE_PASSWORD_LEN, STATE_SCORE_OCC, STATE_SCORE_INC, STATE_SCORE_TARGET,
 STATE_DECISION, STATE_PROFILE, STATE_IMAGE_PROMPT, STATE_VIDEO_SCRIPT, STATE_RESUME,
 STATE_BUSINESS, STATE_CAPTION, STATE_EMAIL, STATE_STUDY) = range(23)

# ─── KEYBOARDS ────────────────────────────────────────────────
def main_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("━━━ 🧠 AI TOOLS ━━━", callback_data="header_ai")],
        [InlineKeyboardButton("🤖 AI Chat", callback_data="chat"),
         InlineKeyboardButton("✍️ AI Writer", callback_data="write")],
        [InlineKeyboardButton("💻 Code Engine", callback_data="code"),
         InlineKeyboardButton("🎨 Image Prompts", callback_data="imgprompt")],
        [InlineKeyboardButton("🎬 Video Scripts", callback_data="videoscript")],
        [InlineKeyboardButton("━━━ 📚 STUDENT ━━━", callback_data="header_student")],
        [InlineKeyboardButton("📖 Study Helper", callback_data="study"),
         InlineKeyboardButton("📝 Summarizer", callback_data="summarize")],
        [InlineKeyboardButton("🌐 Translator", callback_data="translate")],
        [InlineKeyboardButton("━━━ 💼 CAREER ━━━", callback_data="header_career")],
        [InlineKeyboardButton("📄 Resume Builder", callback_data="resume"),
         InlineKeyboardButton("💡 Business Ideas", callback_data="business")],
        [InlineKeyboardButton("📧 Email Writer", callback_data="email"),
         InlineKeyboardButton("📊 Income Score", callback_data="score")],
        [InlineKeyboardButton("━━━ 📱 SOCIAL MEDIA ━━━", callback_data="header_social")],
        [InlineKeyboardButton("📸 Captions & Hashtags", callback_data="caption"),
         InlineKeyboardButton("⚡ Decision Maker", callback_data="decision")],
        [InlineKeyboardButton("━━━ 🎯 PERSONAL ━━━", callback_data="header_personal")],
        [InlineKeyboardButton("📒 Notes", callback_data="notes"),
         InlineKeyboardButton("🔥 Habits", callback_data="habits")],
        [InlineKeyboardButton("💵 Finance", callback_data="finance"),
         InlineKeyboardButton("🔐 Password Gen", callback_data="password")],
        [InlineKeyboardButton("💪 Motivation", callback_data="motivation")],
        [InlineKeyboardButton("━━━ 💎 REWARDS ━━━", callback_data="header_rewards")],
        [InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard"),
         InlineKeyboardButton("🔥 Daily Streak", callback_data="streak")],
        [InlineKeyboardButton("💰 Daily Bonus", callback_data="bonus"),
         InlineKeyboardButton("🤝 Referral", callback_data="referral")],
        [InlineKeyboardButton("👤 My Profile", callback_data="myprofile"),
         InlineKeyboardButton("💎 Premium", callback_data="premium")],
    ])

def back_kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menu", callback_data="menu")]])

def share_kb(text="Share this bot"):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📤 Share Bot", url="https://t.me/share/url?url=https://t.me/NeuroFIuxAI_Bot&text=🧠 Try NeuroFlux AI - The most powerful AI bot on Telegram!")],
        [InlineKeyboardButton("🔙 Menu", callback_data="menu")]
    ])

def premium_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🤝 Invite 5 Friends (FREE Unlock)", callback_data="referral")],
        [InlineKeyboardButton("₹99 One-Time", callback_data="pay_99"),
         InlineKeyboardButton("₹299/mo Pro", callback_data="pay_299")],
        [InlineKeyboardButton("₹999 VIP Lifetime", callback_data="pay_999")],
        [InlineKeyboardButton("🔙 Menu", callback_data="menu")],
    ])

# ─── HELPERS ──────────────────────────────────────────────────
def ensure_user(update):
    u = update.effective_user
    if not db.get_user(u.id):
        db.register_user(u.id, u.username, u.first_name, u.last_name)
    db.update_last_active(u.id)
    db.update_daily_streak(u.id)

def streak_bar(streak):
    filled = min(streak, 7)
    return "🟢" * filled + "⚫" * (7 - filled)

def referral_bar(count):
    filled = min(count, 5)
    return "█" * filled + "░" * (5 - filled)

# ─── /start ───────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    referred_by = None
    if context.args:
        ref_code = context.args[0]
        referrer_id = db.find_user_by_referral_code(ref_code)
        if referrer_id and referrer_id != u.id:
            referred_by = referrer_id

    if not db.get_user(u.id):
        db.register_user(u.id, u.username, u.first_name, u.last_name, referred_by)

    db.update_last_active(u.id)
    streak = db.update_daily_streak(u.id)
    context.user_data.clear()

    msg = (
        f"⚡ *Welcome to NeuroFlux AI*\n\n"
        f"Hey {u.first_name}, you just unlocked the most powerful AI system on Telegram.\n\n"
        f"🧠 *20+ AI Tools* — Chat, Code, Write, Create\n"
        f"📚 *Student Mode* — Ace any exam\n"
        f"💼 *Career Tools* — Resume, Business Ideas, Emails\n"
        f"📱 *Social Media* — Viral captions & scripts\n\n"
        f"🔥 Daily Streak: {streak_bar(streak)} ({streak} days)\n\n"
        f"⚡ *Choose your weapon:*"
    )
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=main_menu_kb())

# ─── /menu ────────────────────────────────────────────────────
async def menu_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_user(update)
    context.user_data.clear()
    await update.message.reply_text("⚡ *NeuroFlux AI — Command Center*\n\nChoose your weapon:", parse_mode="Markdown", reply_markup=main_menu_kb())

# ─── CALLBACK ROUTER ─────────────────────────────────────────
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    ensure_user(update)
    data = query.data
    uid = query.from_user.id

    # Headers - do nothing
    if data.startswith("header_"):
        return

    if data == "menu":
        context.user_data.clear()
        await query.edit_message_text("⚡ *NeuroFlux AI — Command Center*\n\nChoose your weapon:", parse_mode="Markdown", reply_markup=main_menu_kb())

    elif data == "chat":
        context.user_data["state"] = STATE_CHAT
        can_use, remaining = db.check_ai_limit(uid)
        if not can_use:
            await query.edit_message_text("🔒 *Daily limit reached!*\n\nInvite 5 friends to unlock UNLIMITED access.", parse_mode="Markdown", reply_markup=premium_kb())
        else:
            await query.edit_message_text(f"🤖 *AI Chat Active*\n\n💬 Messages left today: {remaining}\n\nSend any message. I remember our conversation.\n\nType /menu to exit.", parse_mode="Markdown", reply_markup=back_kb())

    elif data == "write":
        context.user_data["state"] = STATE_WRITE
        await query.edit_message_text("✍️ *AI Writer*\n\nTell me what to write:\n• Email • Essay • Post • Letter • Story • Anything\n\n📝 Describe what you need:", parse_mode="Markdown", reply_markup=back_kb())

    elif data == "code":
        context.user_data["state"] = STATE_CODE
        await query.edit_message_text("💻 *Code Engine*\n\n🔧 I can:\n• Write code in ANY language\n• Debug your code\n• Explain code\n• Build full projects\n\nPaste your request:", parse_mode="Markdown", reply_markup=back_kb())

    elif data == "imgprompt":
        context.user_data["state"] = STATE_IMAGE_PROMPT
        await query.edit_message_text("🎨 *AI Image Prompt Generator*\n\nDescribe what image you want to create.\n\nI'll generate detailed prompts for Midjourney, DALL-E, or Flux.\n\n💡 Example: 'A cyberpunk city at sunset'", parse_mode="Markdown", reply_markup=back_kb())

    elif data == "videoscript":
        context.user_data["state"] = STATE_VIDEO_SCRIPT
        await query.edit_message_text("🎬 *Viral Video Script Writer*\n\nWhat's your video about?\n\nI'll write a complete script with hook, content, CTA & hashtags.\n\n💡 Works for: YouTube Shorts, Reels, TikTok", parse_mode="Markdown", reply_markup=back_kb())

    elif data == "study":
        context.user_data["state"] = STATE_STUDY
        await query.edit_message_text("📖 *Study Helper*\n\nAsk ANY academic question:\n• Math • Science • History • English\n• Programming • Economics • Any subject\n\n🎯 I explain like a top tutor:", parse_mode="Markdown", reply_markup=back_kb())

    elif data == "summarize":
        context.user_data["state"] = STATE_SUMMARIZE
        await query.edit_message_text("📝 *Summarizer*\n\nPaste any text, article, or document.\n\nI'll extract the key points in seconds.", parse_mode="Markdown", reply_markup=back_kb())

    elif data == "translate":
        context.user_data["state"] = STATE_TRANSLATE_TEXT
        await query.edit_message_text("🌐 *Translator*\n\nSend me the text you want to translate:", parse_mode="Markdown", reply_markup=back_kb())

    elif data == "resume":
        context.user_data["state"] = STATE_RESUME
        await query.edit_message_text("📄 *AI Resume Builder*\n\nTell me about yourself:\n• Your skills\n• Experience\n• Education\n• Job you're targeting\n\n💡 I'll create a professional resume instantly:", parse_mode="Markdown", reply_markup=back_kb())

    elif data == "business":
        context.user_data["state"] = STATE_BUSINESS
        await query.edit_message_text("💡 *Business Idea Generator*\n\nTell me:\n• Your interests/skills\n• Budget (optional)\n• Available time\n\n🚀 I'll generate a money-making idea:", parse_mode="Markdown", reply_markup=back_kb())

    elif data == "email":
        context.user_data["state"] = STATE_EMAIL
        await query.edit_message_text("📧 *AI Email Writer*\n\nDescribe the email you need:\n• Who is it to?\n• What's the purpose?\n• Any specific tone?\n\n✉️ I'll write it perfectly:", parse_mode="Markdown", reply_markup=back_kb())

    elif data == "caption":
        context.user_data["state"] = STATE_CAPTION
        await query.edit_message_text("📸 *Caption & Hashtag Generator*\n\nDescribe your post or niche:\n\n💡 I'll generate viral captions + 30 hashtags + posting tips!", parse_mode="Markdown", reply_markup=back_kb())

    elif data == "score":
        context.user_data["state"] = STATE_SCORE_OCC
        await query.edit_message_text("📊 *Income Score Engine*\n\nWhat do you do? (Your occupation/profession)", parse_mode="Markdown", reply_markup=back_kb())

    elif data == "decision":
        context.user_data["state"] = STATE_DECISION
        await query.edit_message_text("⚡ *Decision Engine*\n\nAsk any question — career, money, life.\nI will give you ONE final decision.", parse_mode="Markdown", reply_markup=back_kb())

    elif data == "notes":
        context.user_data["state"] = STATE_NOTE
        notes = db.get_notes(uid)
        note_text = ""
        if notes:
            note_text = "\n\n📋 *Your Notes:*\n" + "\n".join([f"• {n['note_text']}" for n in notes[:10]])
        await query.edit_message_text(f"📒 *Notes*\n\nSend a note to save it.{note_text}", parse_mode="Markdown", reply_markup=back_kb())

    elif data == "habits":
        habits = db.get_habits(uid)
        kb = []
        for h in habits:
            kb.append([InlineKeyboardButton(f"✅ {h['habit_name']} (🔥{h['streak']})", callback_data=f"hcheck_{h['id']}")])
        kb.append([InlineKeyboardButton("➕ Add Habit", callback_data="habit_add")])
        kb.append([InlineKeyboardButton("🔙 Menu", callback_data="menu")])
        await query.edit_message_text("🔥 *Habit Tracker*\n\nTap a habit to check in:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))

    elif data == "habit_add":
        context.user_data["state"] = STATE_HABIT_ADD
        await query.edit_message_text("➕ *New Habit*\n\nWhat habit do you want to track?", parse_mode="Markdown", reply_markup=back_kb())

    elif data.startswith("hcheck_"):
        hid = int(data.split("_")[1])
        success, streak = db.check_habit(hid)
        if success:
            await query.edit_message_text(f"✅ *Checked!* 🔥 Streak: {streak} days\n\nConsistency is power. Keep going.", parse_mode="Markdown", reply_markup=back_kb())
        else:
            await query.edit_message_text(f"⏳ Already checked today. 🔥 Streak: {streak}\n\nCome back tomorrow.", parse_mode="Markdown", reply_markup=back_kb())

    elif data == "finance":
        inc, exp = db.get_finance_summary(uid)
        balance = inc - exp
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Income", callback_data="fin_income"),
             InlineKeyboardButton("➖ Expense", callback_data="fin_expense")],
            [InlineKeyboardButton("🔙 Menu", callback_data="menu")]
        ])
        await query.edit_message_text(
            f"💵 *Finance Tracker*\n\n💰 Income: ₹{inc:,.0f}\n💸 Expenses: ₹{exp:,.0f}\n📊 Balance: ₹{balance:,.0f}",
            parse_mode="Markdown", reply_markup=kb)

    elif data in ("fin_income", "fin_expense"):
        context.user_data["state"] = STATE_FINANCE_AMT
        context.user_data["fin_type"] = "income" if data == "fin_income" else "expense"
        await query.edit_message_text("💵 Enter amount (number only):", reply_markup=back_kb())

    elif data == "password":
        context.user_data["state"] = STATE_PASSWORD_LEN
        await query.edit_message_text("🔐 *Password Generator*\n\nHow many characters? (8-64)", parse_mode="Markdown", reply_markup=back_kb())

    elif data == "motivation":
        db.increment_total_uses(uid)
        result = ai.ai_motivation()
        await query.edit_message_text(result, parse_mode="Markdown", reply_markup=share_kb())

    elif data == "streak":
        streak = db.get_streak(uid)
        user = db.get_user(uid)
        pts = user["total_points"] if user else 0
        msg = (
            f"🔥 *Daily Streak*\n\n"
            f"Current Streak: {streak} days\n"
            f"{streak_bar(streak)}\n\n"
            f"💰 Points earned from streak: {streak * 2}\n"
            f"📊 Total Points: {pts}\n\n"
            f"⚡ Come back every day to keep your streak alive!\n"
            f"Miss one day = streak resets to 0."
        )
        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=back_kb())

    elif data == "leaderboard":
        leaders = db.get_leaderboard(10)
        msg = "🏆 *LEADERBOARD — Top Players*\n\n"
        medals = ["🥇", "🥈", "🥉"] + ["▪️"] * 7
        for i, l in enumerate(leaders):
            name = l["first_name"] or l["username"] or "Anonymous"
            msg += f"{medals[i]} {name} — {l['total_points']} pts | 🔥{l['daily_streak'] or 0}\n"
        if not leaders:
            msg += "No users yet. Be the first!"
        msg += "\n⚡ Earn points: Daily bonus, streaks, referrals, using tools!"
        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=back_kb())

    elif data == "bonus":
        success, pts = db.claim_daily_bonus(uid)
        if success:
            await query.edit_message_text(f"🎉 *+5 Points!*\n\nTotal: {pts} points\n\n⚡ Come back tomorrow for more!", parse_mode="Markdown", reply_markup=back_kb())
        else:
            await query.edit_message_text("⏳ *Already claimed today.*\n\nCome back in 24 hours.", parse_mode="Markdown", reply_markup=back_kb())

    elif data == "referral":
        ref_code = db.get_referral_code(uid)
        user = db.get_user(uid)
        bot_info = await context.bot.get_me()
        link = f"https://t.me/{bot_info.username}?start={ref_code}"
        ref_count = user['referral_count']
        remaining = max(0, 5 - ref_count)
        bar = referral_bar(ref_count)
        status = '✅ UNLOCKED!' if ref_count >= 5 else f'⚡ {remaining} more to unlock EVERYTHING!'
        msg = (
            f"🤝 *Referral Program*\n\n"
            f"Your link:\n`{link}`\n\n"
            f"Progress: [{bar}] {ref_count}/5\n"
            f"{status}\n\n"
            f"🎁 *You get:* 10 points per referral\n"
            f"🔓 *At 5 referrals:* Unlock ALL premium features FREE\n\n"
            f"📤 Share now and unlock the full power!"
        )
        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=share_kb())

    elif data == "premium":
        await query.edit_message_text(
            "💎 *NeuroFlux Premium*\n\n"
            "🔓 Unlock:\n"
            "• Unlimited AI messages\n"
            "• All 20+ tools unlocked\n"
            "• Priority responses\n"
            "• Full reports & deep analysis\n"
            "• No daily limits\n\n"
            "💡 *FREE WAY:* Invite 5 friends!\n"
            "💳 *Or choose a plan:*",
            parse_mode="Markdown", reply_markup=premium_kb()
        )

    elif data.startswith("pay_"):
        amount = data.split("_")[1]
        plans = {"99": "One-Time Unlock", "299": "Pro Monthly", "999": "VIP Lifetime"}
        await query.edit_message_text(
            f"💳 *{plans.get(amount, 'Premium')} — ₹{amount}*\n\n"
            f"Contact admin for payment & instant activation.\n\n"
            f"Or invite 5 friends to unlock FREE! 🤝",
            parse_mode="Markdown", reply_markup=back_kb()
        )

    elif data == "myprofile":
        user = db.get_user(uid)
        plan_emoji = {"free": "🆓", "basic": "⭐", "pro": "💎", "vip": "👑"}.get(user["plan"], "🆓")
        streak = user["daily_streak"] or 0
        await query.edit_message_text(
            f"👤 *Your Profile*\n\n"
            f"Name: {user['first_name'] or 'N/A'}\n"
            f"Plan: {plan_emoji} {user['plan'].upper()}\n"
            f"Points: {user['total_points']}\n"
            f"Streak: 🔥 {streak} days\n"
            f"Referrals: {user['referral_count']}/5\n"
            f"Unlocked: {'✅' if user['unlocked'] else '🔒'}\n"
            f"Member since: {user['created_at'][:10]}",
            parse_mode="Markdown", reply_markup=back_kb()
        )

# ─── MESSAGE HANDLER ─────────────────────────────────────────
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_user(update)
    state = context.user_data.get("state")
    uid = update.effective_user.id
    text = update.message.text

    if state is None:
        # Default: AI chat
        can_use, remaining = db.check_ai_limit(uid)
        if not can_use:
            await update.message.reply_text("🔒 *Daily limit reached!*\n\nInvite 5 friends for UNLIMITED access.", parse_mode="Markdown", reply_markup=premium_kb())
            return
        history = db.get_chat_history(uid)
        db.save_chat_message(uid, "user", text)
        response = ai.ai_chat(text, history)
        db.save_chat_message(uid, "assistant", response)
        db.increment_ai_usage(uid)
        db.increment_total_uses(uid)
        await update.message.reply_text(response, reply_markup=back_kb())

    elif state == STATE_CHAT:
        can_use, remaining = db.check_ai_limit(uid)
        if not can_use:
            await update.message.reply_text("🔒 *Limit reached.*\n\nInvite friends to unlock unlimited.", parse_mode="Markdown", reply_markup=premium_kb())
            context.user_data["state"] = None
            return
        history = db.get_chat_history(uid)
        db.save_chat_message(uid, "user", text)
        response = ai.ai_chat(text, history)
        db.save_chat_message(uid, "assistant", response)
        db.increment_ai_usage(uid)
        db.increment_total_uses(uid)
        await update.message.reply_text(response, reply_markup=back_kb())

    elif state == STATE_WRITE:
        await update.message.reply_text("⏳ *Crafting...*", parse_mode="Markdown")
        result = ai.ai_write(text)
        db.increment_total_uses(uid)
        context.user_data["state"] = None
        await update.message.reply_text(result, reply_markup=share_kb())

    elif state == STATE_CODE:
        await update.message.reply_text("⏳ *Engineering...*", parse_mode="Markdown")
        result = ai.ai_code(text)
        db.increment_total_uses(uid)
        context.user_data["state"] = None
        await update.message.reply_text(result, reply_markup=back_kb())

    elif state == STATE_IMAGE_PROMPT:
        await update.message.reply_text("⏳ *Generating prompts...*", parse_mode="Markdown")
        result = ai.ai_image_prompt(text)
        db.increment_total_uses(uid)
        context.user_data["state"] = None
        await update.message.reply_text(result, reply_markup=share_kb())

    elif state == STATE_VIDEO_SCRIPT:
        await update.message.reply_text("⏳ *Writing viral script...*", parse_mode="Markdown")
        result = ai.ai_video_script(text)
        db.increment_total_uses(uid)
        context.user_data["state"] = None
        await update.message.reply_text(result, reply_markup=share_kb())

    elif state == STATE_STUDY:
        await update.message.reply_text("⏳ *Solving...*", parse_mode="Markdown")
        result = ai.ai_study(text)
        db.increment_total_uses(uid)
        context.user_data["state"] = None
        await update.message.reply_text(result, reply_markup=share_kb())

    elif state == STATE_SUMMARIZE:
        await update.message.reply_text("⏳ *Extracting key points...*", parse_mode="Markdown")
        result = ai.ai_summarize(text)
        db.increment_total_uses(uid)
        context.user_data["state"] = None
        await update.message.reply_text(result, reply_markup=back_kb())

    elif state == STATE_TRANSLATE_TEXT:
        context.user_data["translate_text"] = text
        context.user_data["state"] = STATE_TRANSLATE_LANG
        await update.message.reply_text("🌐 Which language? (e.g., Hindi, Spanish, French)", reply_markup=back_kb())

    elif state == STATE_TRANSLATE_LANG:
        await update.message.reply_text("⏳ *Translating...*", parse_mode="Markdown")
        result = ai.ai_translate(context.user_data["translate_text"], text)
        db.increment_total_uses(uid)
        context.user_data["state"] = None
        await update.message.reply_text(result, reply_markup=back_kb())

    elif state == STATE_RESUME:
        await update.message.reply_text("⏳ *Building your resume...*", parse_mode="Markdown")
        result = ai.ai_resume(text)
        db.increment_total_uses(uid)
        context.user_data["state"] = None
        await update.message.reply_text(result, reply_markup=share_kb())

    elif state == STATE_BUSINESS:
        await update.message.reply_text("⏳ *Generating business idea...*", parse_mode="Markdown")
        result = ai.ai_business_idea(text)
        db.increment_total_uses(uid)
        context.user_data["state"] = None
        await update.message.reply_text(result, reply_markup=share_kb())

    elif state == STATE_EMAIL:
        await update.message.reply_text("⏳ *Writing email...*", parse_mode="Markdown")
        result = ai.ai_email(text)
        db.increment_total_uses(uid)
        context.user_data["state"] = None
        await update.message.reply_text(result, reply_markup=back_kb())

    elif state == STATE_CAPTION:
        await update.message.reply_text("⏳ *Creating viral content...*", parse_mode="Markdown")
        result = ai.ai_caption(text)
        db.increment_total_uses(uid)
        context.user_data["state"] = None
        await update.message.reply_text(result, reply_markup=share_kb())

    elif state == STATE_SCORE_OCC:
        context.user_data["score_occ"] = text
        context.user_data["state"] = STATE_SCORE_INC
        await update.message.reply_text("💰 Current monthly income? (e.g., ₹30,000)", reply_markup=back_kb())

    elif state == STATE_SCORE_INC:
        context.user_data["score_inc"] = text
        context.user_data["state"] = STATE_SCORE_TARGET
        await update.message.reply_text("🎯 Target monthly income?", reply_markup=back_kb())

    elif state == STATE_SCORE_TARGET:
        context.user_data["score_target"] = text
        await update.message.reply_text("⏳ *Analyzing...*", parse_mode="Markdown")
        result = ai.generate_income_score(
            context.user_data["score_occ"],
            context.user_data["score_inc"],
            context.user_data["score_target"]
        )
        db.save_score(uid, context.user_data["score_occ"], context.user_data["score_inc"], context.user_data["score_target"], 0, result)
        db.increment_total_uses(uid)
        context.user_data["state"] = None
        await update.message.reply_text(result, parse_mode="Markdown", reply_markup=share_kb())

    elif state == STATE_DECISION:
        await update.message.reply_text("⏳ *Processing...*", parse_mode="Markdown")
        result = ai.generate_decision(text)
        db.increment_total_uses(uid)
        context.user_data["state"] = None
        await update.message.reply_text(result, parse_mode="Markdown", reply_markup=back_kb())

    elif state == STATE_PROFILE:
        await update.message.reply_text("⏳ *Scanning...*", parse_mode="Markdown")
        result = ai.scan_profile(text)
        db.increment_total_uses(uid)
        context.user_data["state"] = None
        await update.message.reply_text(result, parse_mode="Markdown", reply_markup=back_kb())

    elif state == STATE_NOTE:
        db.add_note(uid, text)
        await update.message.reply_text("✅ *Note saved!*", parse_mode="Markdown", reply_markup=back_kb())

    elif state == STATE_HABIT_ADD:
        db.add_habit(uid, text)
        context.user_data["state"] = None
        await update.message.reply_text(f"✅ *Habit added:* {text}\n\nCheck in daily to build your streak.", parse_mode="Markdown", reply_markup=back_kb())

    elif state == STATE_FINANCE_AMT:
        try:
            amount = float(text.replace(",", "").replace("₹", "").replace("$", "").strip())
            context.user_data["fin_amount"] = amount
            context.user_data["state"] = STATE_FINANCE_DESC
            await update.message.reply_text("📝 Short description (e.g., Salary, Rent, Food):", reply_markup=back_kb())
        except ValueError:
            await update.message.reply_text("❌ Enter a valid number.", reply_markup=back_kb())

    elif state == STATE_FINANCE_DESC:
        db.add_finance(uid, context.user_data["fin_type"], context.user_data["fin_amount"], text)
        context.user_data["state"] = None
        emoji = "💰" if context.user_data["fin_type"] == "income" else "💸"
        await update.message.reply_text(f"{emoji} *Recorded:* ₹{context.user_data['fin_amount']:,.0f} — {text}", parse_mode="Markdown", reply_markup=back_kb())

    elif state == STATE_PASSWORD_LEN:
        try:
            length = int(text)
            length = max(8, min(64, length))
            chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-="
            password = ''.join(random.choices(chars, k=length))
            context.user_data["state"] = None
            await update.message.reply_text(f"🔐 *Password ({length} chars):*\n\n`{password}`\n\n💡 Save it somewhere safe!", parse_mode="Markdown", reply_markup=back_kb())
        except ValueError:
            await update.message.reply_text("❌ Enter a number (8-64).", reply_markup=back_kb())

    elif state == STATE_BROADCAST:
        if uid != ADMIN_ID:
            return
        all_users = db.get_all_user_ids()
        sent = 0
        for user_id in all_users:
            try:
                await context.bot.send_message(chat_id=user_id, text=text)
                sent += 1
            except Exception:
                pass
        context.user_data["state"] = None
        await update.message.reply_text(f"📢 *Sent to {sent}/{len(all_users)} users.*", parse_mode="Markdown", reply_markup=back_kb())

# ─── ADMIN ────────────────────────────────────────────────────
async def admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    total = db.get_user_count()
    paid = db.get_paid_user_count()
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")],
        [InlineKeyboardButton("🔙 Menu", callback_data="menu")]
    ])
    await update.message.reply_text(
        f"🛡️ *Admin Panel*\n\nTotal: {total}\nPaid: {paid}\nFree: {total - paid}",
        parse_mode="Markdown", reply_markup=kb)

async def admin_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("Unauthorized", show_alert=True)
        return
    await query.answer()
    if query.data == "admin_broadcast":
        context.user_data["state"] = STATE_BROADCAST
        await query.edit_message_text("📢 *Broadcast Mode*\n\nSend the message:", parse_mode="Markdown", reply_markup=back_kb())

# ─── CLEAR ────────────────────────────────────────────────────
async def clear_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db.clear_chat_history(update.effective_user.id)
    await update.message.reply_text("🧹 *Chat memory cleared.*", parse_mode="Markdown", reply_markup=back_kb())

# ─── ERROR HANDLER ────────────────────────────────────────────
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Exception: {context.error}", exc_info=context.error)
    if update and hasattr(update, 'effective_message') and update.effective_message:
        try:
            await update.effective_message.reply_text("⚠️ Something went wrong. Try /menu", reply_markup=back_kb())
        except Exception:
            pass

# ─── MAIN ─────────────────────────────────────────────────────
def main():
    db.init_db()
    logger.info("Starting NeuroFlux AI v2.0...")

    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu_cmd))
    app.add_handler(CommandHandler("admin", admin_cmd))
    app.add_handler(CommandHandler("clear", clear_cmd))

    # Callbacks
    app.add_handler(CallbackQueryHandler(admin_button, pattern="^admin_"))
    app.add_handler(CallbackQueryHandler(button_handler))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    # Error handler
    app.add_error_handler(error_handler)

    # Daily alerts at 9:00 AM
    job_queue = app.job_queue
    if job_queue:
        job_queue.run_daily(daily_alert_job, time=datetime.time(hour=9, minute=0, second=0))

    logger.info("NeuroFlux AI v2.0 is LIVE.")
    app.run_polling(drop_pending_updates=True)

async def daily_alert_job(context: ContextTypes.DEFAULT_TYPE):
    all_users = db.get_all_user_ids()
    alert = ai.get_daily_alert()
    for user_id in all_users:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"🔔 *NeuroFlux Daily*\n\n{alert}",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⚡ Open NeuroFlux", callback_data="menu")]])
            )
        except Exception:
            pass

if __name__ == "__main__":
    main()
