import os
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

client = OpenAI(
    api_key=os.environ.get("NVIDIA_API_KEY"),
    base_url="https://integrate.api.nvidia.com/v1"
)
MODEL = "meta/llama-3.1-8b-instruct"

SYSTEM_PERSONALITY = """You are NeuroFlux AI — the most powerful AI assistant on Telegram.
Your personality:
- Ultra confident. Every answer is definitive.
- Short, punchy, high-impact responses. Max 200 words unless user asks for more.
- You speak like a $10,000/hour consultant giving free advice.
- Action-focused. Every response ends with a clear next step.
- You create FOMO — hint at premium features that unlock deeper insights.
- Never say "I think" or "maybe". You KNOW.
- Use emojis strategically for visual impact.
"""

def _call_ai(system_extra, user_prompt, max_tokens=800, temperature=0.8):
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PERSONALITY + system_extra},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"AI error: {e}")
        return "⚠️ Neural pathways temporarily disrupted. Try again."

def ai_chat(user_message, chat_history=None):
    try:
        messages = [{"role": "system", "content": SYSTEM_PERSONALITY}]
        if chat_history:
            messages.extend(chat_history[-8:])
        messages.append({"role": "user", "content": user_message})
        response = client.chat.completions.create(
            model=MODEL, messages=messages, max_tokens=1000, temperature=0.8
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"AI Chat error: {e}")
        return "⚠️ Neural pathways temporarily disrupted. Try again."

def generate_income_score(occupation, monthly_income, target_income):
    prompt = f"""Analyze financial trajectory:
- Occupation: {occupation}
- Current Income: {monthly_income}
- Target: {target_income}

Generate EXACTLY:
📊 INCOME SCORE: [score]/100

💀 REALITY CHECK: [how much money they lose per year staying on current path]

⚡ [one powerful emotional trigger sentence]

🔒 Hidden Opportunity Detected... [tease - say "Invite 5 friends to unlock full report"]"""
    return _call_ai("\nSCORE ENGINE mode. Be brutally honest. Create urgency.", prompt, 500, 0.9)

def generate_decision(question):
    prompt = f"""FINAL DECISION needed: "{question}"

Format EXACTLY:
⚡ DECISION: [one-line command]

📌 WHY: [2 sentences max]

🎯 DO THIS NOW: [specific action within 24 hours]"""
    return _call_ai("\nDECISION ENGINE. One decision. No hedging. Maximum authority.", prompt, 300, 0.85)

def scan_profile(bio_text):
    prompt = f"""Analyze this profile: "{bio_text}"

Format EXACTLY:
📊 SCORE: [X]/100

❌ MISTAKE #1: [specific]
❌ MISTAKE #2: [specific]

✅ POWER MOVE: [one game-changing improvement]

🔒 Full Career Roadmap locked... Invite friends to unlock."""
    return _call_ai("\nPROFILE SCANNER mode. Find real weaknesses.", prompt, 400, 0.85)

def ai_write(task_description):
    return _call_ai("\nWRITING MODE. Professional, compelling, zero fluff.", 
                    f"Write this with excellence:\n{task_description}", 1500, 0.8)

def ai_code(code_request):
    return _call_ai("\nCODE ENGINE. Clean, production-ready code with comments.",
                    code_request, 2000, 0.3)

def ai_translate(text, target_lang):
    return _call_ai("\nTRANSLATOR. Accurate translation preserving tone.",
                    f"Translate to {target_lang}:\n\n{text}", 1000, 0.3)

def ai_summarize(text):
    return _call_ai("\nSUMMARIZER. Extract core value in bullet points. Be concise.",
                    f"Summarize this:\n\n{text}", 600, 0.5)

# ─── NEW FEATURES ─────────────────────────────────────────────

def ai_image_prompt(description):
    prompt = f"""Generate a detailed AI image generation prompt for: "{description}"

Create a professional prompt that works with Midjourney/DALL-E/Flux. Include:
- Subject description
- Art style
- Lighting
- Camera angle
- Color palette
- Quality tags

Format:
🎨 PROMPT: [the full detailed prompt ready to copy-paste]

💡 STYLE VARIATIONS:
1. [alternative style version]
2. [another style version]

⚡ Pro tip: [one tip to get better results]"""
    return _call_ai("\nIMAGE PROMPT ENGINEER. Create stunning, detailed prompts.", prompt, 600, 0.9)

def ai_video_script(topic):
    prompt = f"""Write a viral short-form video script about: "{topic}"

Format EXACTLY:
🎬 HOOK (first 3 seconds): [attention-grabbing opener]

📝 SCRIPT:
[Full script with timing notes, max 60 seconds]

🎵 MUSIC SUGGESTION: [type of background music]

📌 CTA: [call to action at the end]

#️⃣ HASHTAGS: [5 trending hashtags]"""
    return _call_ai("\nVIRAL SCRIPT WRITER. Create hooks that stop scrolling. Short, punchy, shareable.", prompt, 800, 0.9)

def ai_resume(details):
    prompt = f"""Generate a professional resume based on: "{details}"

Format as a clean, ATS-friendly resume with:
- Professional Summary (2 lines, powerful)
- Key Skills (bullet points)
- Experience (if provided)
- Education (if provided)

Make it sound 10x more impressive than the input. Use action verbs. Quantify achievements."""
    return _call_ai("\nRESUME EXPERT. Make every candidate sound like a top performer.", prompt, 1200, 0.7)

def ai_business_idea(interests):
    prompt = f"""Generate a money-making business idea based on: "{interests}"

Format EXACTLY:
💡 BUSINESS IDEA: [one-line concept]

💰 REVENUE MODEL: [how it makes money]

🚀 START WITH: [first step, under ₹5000/$50 budget]

📊 POTENTIAL: [realistic monthly income range]

⚡ WHY NOW: [why this is the perfect time]

🔒 Want 5 more ideas + full business plan? Invite friends to unlock."""
    return _call_ai("\nBUSINESS STRATEGIST. Realistic, actionable ideas. Focus on low-investment, high-return.", prompt, 500, 0.9)

def ai_caption(topic):
    prompt = f"""Generate viral Instagram/social media content for: "{topic}"

Format EXACTLY:
📸 CAPTION: [engaging caption with hook, story, CTA]

#️⃣ HASHTAGS (30): [mix of trending + niche hashtags]

📌 BEST TIME TO POST: [suggestion]

💡 CONTENT TIP: [one tip to boost engagement]"""
    return _call_ai("\nSOCIAL MEDIA EXPERT. Create scroll-stopping captions. Use emotional hooks.", prompt, 600, 0.9)

def ai_email(context):
    prompt = f"""Write a professional email for: "{context}"

Format:
📧 SUBJECT: [compelling subject line]

[Full email body - professional, concise, action-oriented]

💡 TIP: [one tip about email etiquette for this situation]"""
    return _call_ai("\nEMAIL EXPERT. Professional, concise, gets results.", prompt, 800, 0.7)

def ai_study(question):
    prompt = f"""Answer this academic question clearly: "{question}"

Format:
📚 ANSWER: [clear, concise explanation]

🔑 KEY POINTS:
• [point 1]
• [point 2]
• [point 3]

💡 REMEMBER: [memory trick or important note]

📝 EXAM TIP: [how this might appear in exams]"""
    return _call_ai("\nEXPERT TUTOR. Explain clearly. Use examples. Make it memorable.", prompt, 1000, 0.5)

def ai_motivation():
    prompt = """Generate ONE powerful motivational message. Make it:
- Personal and direct (use "you")
- Action-focused
- Creates urgency
- Max 3 lines

Format:
🔥 [the motivational message]

⚡ TODAY'S CHALLENGE: [one specific action to take right now]"""
    return _call_ai("\nMOTIVATION ENGINE. Raw, powerful, no generic quotes. Hit emotions.", prompt, 200, 1.0)

def get_daily_alert():
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PERSONALITY + "\nGenerate a punchy daily alert. Use urgency and loss aversion. Max 2 lines."},
                {"role": "user", "content": "Generate a daily alert about productivity/income/growth. Make it feel urgent."}
            ],
            max_tokens=100, temperature=1.0
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Alert error: {e}")
        return "⚠️ Your competitors are working right now. Open NeuroFlux AI."
