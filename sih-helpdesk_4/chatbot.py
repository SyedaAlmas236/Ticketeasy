import os
import urllib.parse
from openai import AsyncOpenAI

# --- CONFIGURATION ---
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "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")
MODEL_NAME = "meta/llama-3.1-8b-instruct"

aclient = AsyncOpenAI(
    base_url="https://integrate.api.nvidia.com/v1", 
    api_key=NVIDIA_API_KEY
)

# --- SYSTEM PROMPT ---
CHAT_SYSTEM_PROMPT = """
You are the Official IT Support AI for PowerGrid (PGCIL).

RULES:
1. HELP FIRST: Try to solve the user's issue (WiFi, VPN, Password) using your knowledge.
2. ASK BEFORE ACTION: If you cannot solve it, ask: "Would you like to raise a ticket?"
3. FORMAT: Use bullet points ( * ) for clarity.
4. TONE: Professional and concise.
"""

def check_special_intents(message, history):
    """
    Checks for intents. Only redirects on EXPLICIT commands.
    """
    msg = message.lower()

    # --- SAFETY CHECKS (Do NOT redirect on these) ---
    if "how" in msg or "where" in msg: return None # User is asking a question
    if "don't" in msg or "do not" in msg: return None # User is refusing
    if "wait" in msg or "no" in msg: return None

    # --- 1. RAISE TICKET REDIRECT ---
    # Trigger only on strong action verbs + "ticket"
    if (("raise" in msg or "create" in msg or "submit" in msg or "file" in msg) and "ticket" in msg) or \
       ("yes" in msg and "raise" in msg):
        
        # --- SMART CONTEXT EXTRACTION ---
        prefill_subject = "Issue Reported via Chatbot"
        prefill_desc = ""

        # Look for the ACTUAL problem in history (Skip the "Raise ticket" message)
        if history and len(history) > 0:
            for old_msg in reversed(history):
                content = old_msg.get("content", "")
                role = old_msg.get("role", "")
                
                # We want the last USER message that ISN'T the command "raise ticket"
                if role == "user" and "raise" not in content.lower() and "ticket" not in content.lower():
                    prefill_desc = content
                    break
        
        # Fallback: If no history, just use the current message (though unlikely)
        if not prefill_desc:
            prefill_desc = "User requested ticket via chatbot."

        # Encode for URL
        safe_subject = urllib.parse.quote(prefill_subject)
        safe_desc = urllib.parse.quote(prefill_desc)

        return {
            "text": "Understood. I am redirecting you to the ticket form with your details pre-filled.",
            "redirect": f"/tickets/new?subject={safe_subject}&description={safe_desc}"
        }

    # --- 2. DASHBOARD REDIRECT ---
    if "dashboard" in msg or "my tickets" in msg or "check status" in msg:
        return {
            "text": "Opening your Dashboard...",
            "redirect": "/employee/home"
        }

    # --- 3. LOGIN REDIRECT ---
    if "login" in msg or "sign in" in msg:
        return {
            "text": "Taking you to the Login page...",
            "redirect": "/auth?tab=login"
        }

    return None

async def get_chat_response(user_message: str, history: list = None) -> dict:
    if history is None: history = []
    
    # 1. Check intent WITH history
    special_action = check_special_intents(user_message, history)
    if special_action:
        return special_action

    # 2. If no intent, ask AI
    messages = [{"role": "system", "content": CHAT_SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    try:
        response = await aclient.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.3, 
            max_tokens=300,
            top_p=1
        )
        return {"text": response.choices[0].message.content, "redirect": None}

    except Exception:
        return {"text": "* System Error: Could not connect to AI.", "redirect": None}