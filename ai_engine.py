import os
import logging
from openai import OpenAI

NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY")
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"

logger = logging.getLogger(__name__)

client = OpenAI(
    api_key=NVIDIA_API_KEY,
    base_url=NVIDIA_BASE_URL
)
MODEL = "nv-llama2-70b"

SYSTEM_PERSONALITY = """You are NeuroFlux AI — an elite, authoritative AI intelligence system. 
Your personality:
- Confident and commanding. Never uncertain.
- Slightly mysterious. You hint at knowing more than you reveal.
- Authority-driven. You speak like a strategist who has seen it all.
- High-value tone. Every word carries weight.
- Never casual. Never use filler words.
- Direct and action-focused. No fluff.
- You create curiosity gaps — always leave the user wanting more.
- You speak like a mentor who charges $10,000/hour but is giving a rare free glimpse.
"""

def ai_chat(user_message, chat_history=None):
    try:
        messages = [{"role": "system", "content": SYSTEM_PERSONALITY}]
        if chat_history:
            messages.extend(chat_history[-8:])
        messages.append({"role": "user", "content": user_message})
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=1000,
            temperature=0.8
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"AI Chat error: {e}")
        return "⚠️ Neural pathways temporarily disrupted. Try again."

def generate_income_score(occupation, monthly_income, target_income):
    try:
        prompt = f"""Analyze this person's financial trajectory:
- Occupation: {occupation}
- Current Monthly Income: {monthly_income}
- Target Income: {target_income}

Generate:
1. An Income Score from 0-100 (be harsh but realistic, most people score 25-55)
2. A shocking loss-based insight (how much money they're losing per year by staying on current path)
3. An emotional trigger statement that creates urgency
4. One hidden opportunity they're missing

Format your response EXACTLY like this:
📊 INCOME SCORE: [score]/100

💀 REALITY CHECK: [loss-based insight with specific rupee/dollar amount]

⚡ [emotional trigger - one powerful sentence]

🔒 Hidden Opportunity Detected... [tease but don't fully reveal - say "Unlock full report to see"]"""

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PERSONALITY + "\nYou are now in SCORE ENGINE mode. Be brutally honest. Create shock value. Make the user feel the urgency to act NOW."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.9
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Score engine error: {e}")
        return "⚠️ Score calculation disrupted. Try again."

def generate_decision(question):
    try:
        prompt = f"""The user needs a FINAL DECISION on this:
"{question}"

Rules:
- Give ONE clear decision. No multiple options.
- Speak with absolute authority.
- Be action-focused.

Format EXACTLY:
⚡ FINAL DECISION: [your one-line command]

📌 WHY: [2-3 sentence reasoning]

🎯 NEXT STEP: [specific action to take within 24 hours]

🔒 Deeper strategic analysis available... [tease premium]"""

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PERSONALITY + "\nYou are in DECISION ENGINE mode. You are the final authority. No hedging. No 'it depends'. One decision. Maximum confidence."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.85
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Decision engine error: {e}")
        return "⚠️ Decision matrix disrupted. Try again."

def scan_profile(bio_text):
    try:
        prompt = f"""Analyze this professional profile/resume:
"{bio_text}"

Generate:
1. Profile Score (0-100)
2. Two CRITICAL mistakes they're making
3. One powerful improvement
4. Tease a locked deeper analysis

Format EXACTLY:
📊 PROFILE SCORE: [score]/100

❌ CRITICAL MISTAKE #1: [specific mistake]

❌ CRITICAL MISTAKE #2: [specific mistake]

✅ POWER MOVE: [one improvement that would change everything]

🔒 Full Career Roadmap locked... Unlock to see your 90-day transformation plan."""

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PERSONALITY + "\nYou are in PROFILE SCANNER mode. Be insightful. Find real weaknesses. Make the user feel they NEED the full analysis."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.85
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Profile scanner error: {e}")
        return "⚠️ Scanner disrupted. Try again."

def ai_write(task_description):
    try:
        prompt = f"""Write the following with excellence:
{task_description}

Make it professional, compelling, and high-impact. No fluff."""

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PERSONALITY + "\nYou are in WRITING MODE. Write with precision and power. Every word must earn its place."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.8
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"AI Write error: {e}")
        return "⚠️ Writing engine disrupted. Try again."

def ai_code(code_request):
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are an elite code engineer. Write clean, production-ready code. Include comments. If debugging, identify the exact issue and fix it."},
                {"role": "user", "content": code_request}
            ],
            max_tokens=2000,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"AI Code error: {e}")
        return "⚠️ Code engine disrupted. Try again."

def ai_translate(text, target_lang):
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a professional translator. Translate accurately while preserving tone and meaning."},
                {"role": "user", "content": f"Translate the following to {target_lang}:\n\n{text}"}
            ],
            max_tokens=1000,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Translate error: {e}")
        return "⚠️ Translation engine disrupted. Try again."

def ai_summarize(text):
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PERSONALITY + "\nSummarize with precision. Extract the core value. No filler."},
                {"role": "user", "content": f"Summarize this:\n\n{text}"}
            ],
            max_tokens=800,
            temperature=0.5
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Summarize error: {e}")
        return "⚠️ Summary engine disrupted. Try again."

def get_daily_alert():
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PERSONALITY + "\nGenerate a short, punchy daily alert that triggers emotion and brings the user back. Use urgency. Use loss aversion. Max 2-3 lines."},
                {"role": "user", "content": "Generate a daily alert notification for a user about their income/career/productivity. Make it feel urgent and personal."}
            ],
            max_tokens=150,
            temperature=1.0
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Alert error: {e}")
        return "⚠️ Your income trajectory needs attention. Open NeuroFlux AI now."
