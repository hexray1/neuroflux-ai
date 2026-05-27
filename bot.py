import logging
import asyncio
import random
import string
import datetime
import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    CallbackQueryHandler, ConversationHandler, ContextTypes
)

import database as db
import ai_engine as ai

# ─── CONFIG (Railway env vars) ────────────────────────────────
TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "5350231648"))

# ─── LOGGING ───────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("NeuroFlux")

# ─── STATES ────────────────────────────────────────────────────
(STATE_SCORE_OCC, STATE_SCORE_INC, STATE_SCORE_TARGET,
 STATE_DECISION, STATE_PROFILE, STATE_CHAT,
 STATE_WRITE, STATE_CODE, STATE_TRANSLATE_TEXT, STATE_TRANSLATE_LANG,
 STATE_SUMMARIZE, STATE_NOTE, STATE_HABIT_ADD, STATE_HABIT_CHECK,
 STATE_FINANCE_TYPE, STATE_FINANCE_AMT, STATE_FINANCE_DESC,
 STATE_BROADCAST, STATE_PASSWORD_LEN) = range(19)

# ─── KEYBOARDS ─────────────────────────────────────────────────
def main_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 Income Score", callback_data="score"),
         InlineKeyboardButton("📊 Profile Scan", callback_data="profile")],
        [InlineKeyboardButton("⚡ Get Decision", callback_data="decision"),
         InlineKeyboardButton("🤖 AI Chat", callback_data="chat")],
        [InlineKeyboardButton("✍️ AI Writer", callback_data="write"),
         InlineKeyboardButton("💻 Code Engine", callback_data="code")],
        [InlineKeyboardButton("🌐 Translator", callback_data="translate"),
         InlineKeyboardButton("📝 Summarizer", callback_data="summarize")],
        [InlineKeyboardButton("📒 Notes", callback_data="notes"),
         InlineKeyboardButton("🔥 Habits", callback_data="habits")],
        [InlineKeyboardButton("💵 Finance", callback_data="finance"),
         InlineKeyboardButton("🔐 Password Gen", callback_data="password")],
        [InlineKeyboardButton("💰 Daily Bonus", callback_data="bonus"),
         InlineKeyboardButton("💎 Premium", callback_data="premium")],
        [InlineKeyboardButton("🤝 Referral Link", callback_data="referral"),
         InlineKeyboardButton("👤 My Profile", callback_data="myprofile")],
    ])

def back_kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")]])

def premium_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("₹99 One-Time Unlock", callback_data="pay_99")],
        [InlineKeyboardButton("₹299/month Pro", callback_data="pay_299")],
        [InlineKeyboardButton("₹999 VIP Lifetime", callback_data="pay_999")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")],
    ])

# ─── HELPERS ───────────────────────────────────────────────────
def ensure_user(update):
    u = update.effective_user
    if not db.get_user(u.id):
        db.register_user(u.id, u.username, u.first_name, u.last_name)
    db.update_last_active(u.id)

# ─── /start ────────────────────────────────────────────────────
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
    context.user_data.clear()

    msg = (
        f"⚡ *Your future income is already decided.*\n"
        f"Let AI reveal it.\n\n"
        f"Welcome, {u.first_name}. You've entered *NeuroFlux AI* — "
        f"an elite intelligence system designed to decode your financial destiny.\n\n"
        f"Choose your weapon:"
    )
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=main_menu_kb())

# ─── /menu ─────────────────────────────────────────────────────
async def menu_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_user(update)
    context.user_data.clear()
    await update.message.reply_text("⚡ *NeuroFlux AI — Command Center*\n\nChoose your weapon:", parse_mode="Markdown", reply_markup=main_menu_kb())

# ─── /profile ──────────────────────────────────────────────────
async def profile_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_user(update)
    user = db.get_user(update.effective_user.id)
    plan_emoji = {"free": "🆓", "basic": "⭐", "pro": "💎", "vip": "👑"}.get(user["plan"], "🆓")
    msg = (
        f"👤 *Your Profile*\n\n"
        f"Name: {user['first_name'] or 'N/A'}\n"
        f"Plan: {plan_emoji} {user['plan'].upper()}\n"
        f"Points: {user['total_points']}\n"
        f"Referrals: {user['referral_count']}\n"
        f"Unlocked: {'✅' if user['unlocked'] else '🔒'}\n"
        f"Member since: {user['created_at'][:10]}"
    )
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=back_kb())

# ─── CALLBACK ROUTER ──────────────────────────────────────────
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    ensure_user(update)
    data = query.data
    uid = query.from_user.id

    if data == "menu":
        context.user_data.clear()
        await query.edit_message_text("⚡ *NeuroFlux AI — Command Center*\n\nChoose your weapon:", parse_mode="Markdown", reply_markup=main_menu_kb())

    elif data == "score":
        context.user_data["state"] = STATE_SCORE_OCC
        await query.edit_message_text("🔍 *Income Score Engine*\n\nWhat do you do? (Your occupation/profession)", parse_mode="Markdown", reply_markup=back_kb())

    elif data == "profile":
        context.user_data["state"] = STATE_PROFILE
        await query.edit_message_text("📊 *Profile Scanner*\n\nPaste your resume, bio, or professional summary below.", parse_mode="Markdown", reply_markup=back_kb())

    elif data == "decision":
        context.user_data["state"] = STATE_DECISION
        await query.edit_message_text("⚡ *Decision Engine*\n\nAsk any question — career, money, life.\nI will give you ONE final decision.", parse_mode="Markdown", reply_markup=back_kb())

    elif data == "chat":
        context.user_data["state"] = STATE_CHAT
        can_use, remaining = db.check_ai_limit(uid)
        if not can_use:
            await query.edit_message_text("🔒 *Daily limit reached (5/5)*\n\nUpgrade to Premium for unlimited AI access.", parse_mode="Markdown", reply_markup=premium_kb())
        else:
            await query.edit_message_text(f"🤖 *AI Chat Active*\n\nMessages remaining: {remaining}\nSend any message. Type /menu to exit.\n\nI remember our conversation.", parse_mode="Markdown", reply_markup=back_kb())

    elif data == "write":
        context.user_data["state"] = STATE_WRITE
        await query.edit_message_text("✍️ *AI Writer*\n\nTell me what to write:\n• Email\n• Essay\n• Social media post\n• Cover letter\n• Anything\n\nDescribe what you need:", parse_mode="Markdown", reply_markup=back_kb())

    elif data == "code":
        context.user_data["state"] = STATE_CODE
        await query.edit_message_text("💻 *Code Engine*\n\nDescribe what you need:\n• Write code in any language\n• Debug existing code\n• Explain code\n\nPaste your request:", parse_mode="Markdown", reply_markup=back_kb())

    elif data == "translate":
        context.user_data["state"] = STATE_TRANSLATE_TEXT
        await query.edit_message_text("🌐 *Translator*\n\nSend me the text you want to translate:", parse_mode="Markdown", reply_markup=back_kb())

    elif data == "summarize":
        context.user_data["state"] = STATE_SUMMARIZE
        await query.edit_message_text("📝 *Summarizer*\n\nPaste the text or article you want summarized:", parse_mode="Markdown", reply_markup=back_kb())

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
        kb.append([InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")])
        await query.edit_message_text("🔥 *Habit Tracker*\n\nTap a habit to check in today:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))

    elif data == "habit_add":
        context.user_data["state"] = STATE_HABIT_ADD
        await query.edit_message_text("➕ *New Habit*\n\nWhat habit do you want to track?", parse_mode="Markdown", reply_markup=back_kb())

    elif data.startswith("hcheck_"):
        hid = int(data.split("_")[1])
        success, streak = db.check_habit(hid)
        if success:
            await query.edit_message_text(f"✅ *Habit checked!*\n\n🔥 Current streak: {streak} days\n\nKeep going. Consistency is power.", parse_mode="Markdown", reply_markup=back_kb())
        else:
            await query.edit_message_text(f"⏳ Already checked today.\n\n🔥 Streak: {streak} days\n\nCome back tomorrow.", parse_mode="Markdown", reply_markup=back_kb())

    elif data == "finance":
        inc, exp = db.get_finance_summary(uid)
        balance = inc - exp
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add Income", callback_data="fin_income"),
             InlineKeyboardButton("➖ Add Expense", callback_data="fin_expense")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")]
        ])
        await query.edit_message_text(
            f"💵 *Finance Tracker*\n\n"
            f"💰 Income: ₹{inc:,.0f}\n"
            f"💸 Expenses: ₹{exp:,.0f}\n"
            f"📊 Balance: ₹{balance:,.0f}",
            parse_mode="Markdown", reply_markup=kb
        )

    elif data in ("fin_income", "fin_expense"):
        context.user_data["state"] = STATE_FINANCE_AMT
        context.user_data["fin_type"] = "income" if data == "fin_income" else "expense"
        await query.edit_message_text(f"💵 Enter the amount (number only):", reply_markup=back_kb())

    elif data == "password":
        context.user_data["state"] = STATE_PASSWORD_LEN
        await query.edit_message_text("🔐 *Password Generator*\n\nHow many characters? (8-64)", parse_mode="Markdown", reply_markup=back_kb())

    elif data == "bonus":
        success, pts = db.claim_daily_bonus(uid)
        if success:
            await query.edit_message_text(f"🎉 *Daily Bonus Claimed!*\n\n+5 points\nTotal: {pts} points", parse_mode="Markdown", reply_markup=back_kb())
        else:
            await query.edit_message_text("⏳ *Already claimed today.*\n\nCome back tomorrow for your next bonus.", parse_mode="Markdown", reply_markup=back_kb())

    elif data == "premium":
        await query.edit_message_text(
            "💎 *NeuroFlux Premium*\n\n"
            "Unlock the full power:\n"
            "• Unlimited AI Chat\n"
            "• Full Score Reports\n"
            "• Deep Profile Analysis\n"
            "• Priority Responses\n"
            "• Exclusive Insights\n\n"
            "Choose your plan:",
            parse_mode="Markdown", reply_markup=premium_kb()
        )

    elif data.startswith("pay_"):
        amount = data.split("_")[1]
        plans = {"99": "One-Time Unlock", "299": "Pro Monthly", "999": "VIP Lifetime"}
        await query.edit_message_text(
            f"💳 *{plans.get(amount, 'Premium')} — ₹{amount}*\n\n"
            f"Payment integration coming soon.\n"
            f"Contact admin for manual activation.\n\n"
            f"🔒 Your account will be upgraded instantly after payment.",
            parse_mode="Markdown", reply_markup=back_kb()
        )

    elif data == "referral":
        ref_code = db.get_referral_code(uid)
        user = db.get_user(uid)
        bot_info = await context.bot.get_me()
        link = f"https://t.me/{bot_info.username}?start={ref_code}"
        ref_count = user['referral_count']
        remaining = 3 - ref_count
        status = '✅ Unlocked!' if ref_count >= 3 else f'Invite {remaining} more to unlock full reports!'
        await query.edit_message_text(
            f"🤝 *Your Referral Link*\n\n"
            f"`{link}`\n\n"
            f"Referrals: {ref_count}/3\n"
            f"{status}\n\n"
            f"Share this link. When 3 people join, you unlock everything for free.",
            parse_mode="Markdown", reply_markup=back_kb()
        )

    elif data == "myprofile":
        user = db.get_user(uid)
        plan_emoji = {"free": "🆓", "basic": "⭐", "pro": "💎", "vip": "👑"}.get(user["plan"], "🆓")
        await query.edit_message_text(
            f"👤 *Your Profile*\n\n"
            f"Name: {user['first_name'] or 'N/A'}\n"
            f"Plan: {plan_emoji} {user['plan'].upper()}\n"
            f"Points: {user['total_points']}\n"
            f"Referrals: {user['referral_count']}\n"
            f"Unlocked: {'✅' if user['unlocked'] else '🔒'}\n"
            f"Member since: {user['created_at'][:10]}",
            parse_mode="Markdown", reply_markup=back_kb()
        )

# ─── MESSAGE HANDLER ──────────────────────────────────────────
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_user(update)
    state = context.user_data.get("state")
    uid = update.effective_user.id
    text = update.message.text

    if state is None:
        # Default: treat as AI chat
        can_use, remaining = db.check_ai_limit(uid)
        if not can_use:
            await update.message.reply_text("🔒 *Daily limit reached (5/5)*\n\nUpgrade to Premium for unlimited access.", parse_mode="Markdown", reply_markup=premium_kb())
            return
        history = db.get_chat_history(uid)
        db.save_chat_message(uid, "user", text)
        response = ai.ai_chat(text, history)
        db.save_chat_message(uid, "assistant", response)
        db.increment_ai_usage(uid)
        await update.message.reply_text(response, reply_markup=back_kb())

    elif state == STATE_SCORE_OCC:
        context.user_data["score_occ"] = text
        context.user_data["state"] = STATE_SCORE_INC
        await update.message.reply_text("💰 What's your current monthly income? (e.g., ₹30,000 or $2,000)", reply_markup=back_kb())

    elif state == STATE_SCORE_INC:
        context.user_data["score_inc"] = text
        context.user_data["state"] = STATE_SCORE_TARGET
        await update.message.reply_text("🎯 What's your target monthly income?", reply_markup=back_kb())

    elif state == STATE_SCORE_TARGET:
        context.user_data["score_target"] = text
        await update.message.reply_text("⏳ *Analyzing your financial DNA...*", parse_mode="Markdown")
        result = ai.generate_income_score(
            context.user_data["score_occ"],
            context.user_data["score_inc"],
            context.user_data["score_target"]
        )
        db.save_score(uid, context.user_data["score_occ"], context.user_data["score_inc"], context.user_data["score_target"], 0, result)
        
        lock_msg = ""
        if not db.is_unlocked(uid):
            lock_msg = "\n\n🔒 *Full report locked.*\nUnlock by inviting 3 friends or upgrading to Premium."
        
        context.user_data["state"] = None
        await update.message.reply_text(result + lock_msg, parse_mode="Markdown", reply_markup=back_kb())

    elif state == STATE_DECISION:
        await update.message.reply_text("⏳ *Processing through decision matrix...*", parse_mode="Markdown")
        result = ai.generate_decision(text)
        lock_msg = ""
        if not db.is_unlocked(uid):
            lock_msg = "\n\n🔒 *Strategic deep-dive locked.* Unlock for full analysis."
        context.user_data["state"] = None
        await update.message.reply_text(result + lock_msg, parse_mode="Markdown", reply_markup=back_kb())

    elif state == STATE_PROFILE:
        await update.message.reply_text("⏳ *Scanning profile...*", parse_mode="Markdown")
        result = ai.scan_profile(text)
        context.user_data["state"] = None
        await update.message.reply_text(result, parse_mode="Markdown", reply_markup=back_kb())

    elif state == STATE_CHAT:
        can_use, remaining = db.check_ai_limit(uid)
        if not can_use:
            await update.message.reply_text("🔒 *Daily limit reached.*\n\nUpgrade to Premium.", parse_mode="Markdown", reply_markup=premium_kb())
            context.user_data["state"] = None
            return
        history = db.get_chat_history(uid)
        db.save_chat_message(uid, "user", text)
        response = ai.ai_chat(text, history)
        db.save_chat_message(uid, "assistant", response)
        db.increment_ai_usage(uid)
        await update.message.reply_text(response, reply_markup=back_kb())

    elif state == STATE_WRITE:
        await update.message.reply_text("⏳ *Crafting...*", parse_mode="Markdown")
        result = ai.ai_write(text)
        context.user_data["state"] = None
        await update.message.reply_text(result, reply_markup=back_kb())

    elif state == STATE_CODE:
        await update.message.reply_text("⏳ *Engineering...*", parse_mode="Markdown")
        result = ai.ai_code(text)
        context.user_data["state"] = None
        await update.message.reply_text(result, reply_markup=back_kb())

    elif state == STATE_TRANSLATE_TEXT:
        context.user_data["translate_text"] = text
        context.user_data["state"] = STATE_TRANSLATE_LANG
        await update.message.reply_text("🌐 Which language to translate to? (e.g., Hindi, Spanish, French)", reply_markup=back_kb())

    elif state == STATE_TRANSLATE_LANG:
        await update.message.reply_text("⏳ *Translating...*", parse_mode="Markdown")
        result = ai.ai_translate(context.user_data["translate_text"], text)
        context.user_data["state"] = None
        await update.message.reply_text(result, reply_markup=back_kb())

    elif state == STATE_SUMMARIZE:
        await update.message.reply_text("⏳ *Extracting core insights...*", parse_mode="Markdown")
        result = ai.ai_summarize(text)
        context.user_data["state"] = None
        await update.message.reply_text(result, reply_markup=back_kb())

    elif state == STATE_NOTE:
        db.add_note(uid, text)
        await update.message.reply_text("✅ *Note saved.*", parse_mode="Markdown", reply_markup=back_kb())

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
            await update.message.reply_text(f"🔐 *Generated Password ({length} chars):*\n\n`{password}`", parse_mode="Markdown", reply_markup=back_kb())
        except ValueError:
            await update.message.reply_text("❌ Enter a valid number (8-64).", reply_markup=back_kb())

    elif state == STATE_BROADCAST:
        if uid != ADMIN_ID:
            await update.message.reply_text("❌ Unauthorized.", reply_markup=back_kb())
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
        await update.message.reply_text(f"📢 *Broadcast sent to {sent}/{len(all_users)} users.*", parse_mode="Markdown", reply_markup=back_kb())

# ─── ADMIN COMMANDS ────────────────────────────────────────────
async def admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized.")
        return
    total = db.get_user_count()
    paid = db.get_paid_user_count()
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")]
    ])
    await update.message.reply_text(
        f"🛡️ *Admin Panel*\n\n"
        f"Total Users: {total}\n"
        f"Paid Users: {paid}\n"
        f"Free Users: {total - paid}",
        parse_mode="Markdown", reply_markup=kb
    )

async def admin_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("Unauthorized", show_alert=True)
        return
    await query.answer()
    if query.data == "admin_broadcast":
        context.user_data["state"] = STATE_BROADCAST
        await query.edit_message_text("📢 *Broadcast Mode*\n\nSend the message to broadcast to all users:", parse_mode="Markdown", reply_markup=back_kb())

# ─── DAILY ALERTS JOB ─────────────────────────────────────────
async def daily_alert_job(context: ContextTypes.DEFAULT_TYPE):
    logger.info("Running daily alerts...")
    all_users = db.get_all_user_ids()
    alert = ai.get_daily_alert()
    sent = 0
    for user_id in all_users:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"🔔 *NeuroFlux Daily Alert*\n\n{alert}",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Open NeuroFlux", callback_data="menu")]])
            )
            sent += 1
        except Exception:
            pass
    logger.info(f"Daily alerts sent to {sent}/{len(all_users)} users.")

# ─── CLEAR CHAT ────────────────────────────────────────────────
async def clear_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db.clear_chat_history(update.effective_user.id)
    await update.message.reply_text("🧹 *Chat memory cleared.*", parse_mode="Markdown", reply_markup=back_kb())

# ─── ERROR HANDLER ─────────────────────────────────────────────
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Exception: {context.error}", exc_info=context.error)
    if update and hasattr(update, 'effective_message') and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "⚠️ Something went wrong. Try again or use /menu to restart.",
                reply_markup=back_kb()
            )
        except Exception:
            pass

# ─── MAIN ──────────────────────────────────────────────────────
def main():
    db.init_db()
    logger.info("Starting NeuroFlux AI...")

    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu_cmd))
    app.add_handler(CommandHandler("profile", profile_cmd))
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
        logger.info("Daily alert job scheduled for 9:00 AM.")

    logger.info("NeuroFlux AI is LIVE.")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
