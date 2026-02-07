# ai_engine.py
import os
import json
import re
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from openai import AsyncOpenAI
from redis.asyncio import Redis

# --- CONFIGURATION ---
# [WARN] Load API Key from environment variable for security
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "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")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
MODEL_NAME = "meta/llama-3.1-8b-instruct"

# --- CLIENTS ---
aclient = AsyncOpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=NVIDIA_API_KEY)
redis_client = Redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)

# --- DOMAIN MODELS ---
class TicketAnalysis(BaseModel):
    summary: str = Field(..., description="Very short summary")
    category: str
    priority: str
    sentiment: str
    suggested_steps: List[str]

    @field_validator('category', mode='before')
    @classmethod
    def normalize_category(cls, v):
        v_lower = v.lower()
        if "hardware" in v_lower: return "hardware"
        if "network" in v_lower: return "network"
        if "data" in v_lower or "db" in v_lower: return "database"
        return "software"

    @field_validator('priority', mode='before')
    @classmethod
    def normalize_priority(cls, v):
        v_lower = v.lower()
        if "critical" in v_lower or "urgent" in v_lower or "furious" in v_lower: return "high"
        if "high" in v_lower: return "high"
        if "low" in v_lower: return "low"
        return "medium"

# --- SYSTEM PROMPT WITH 10 SENTIMENTS ---
SYSTEM_PROMPT = """
You are an IT Triage Bot.
Analyze the ticket content (Subject and Description).
Output ONLY raw JSON. No markdown.

1. CLASSIFY into exactly one category: hardware, software, network, database.
2. DETECT sentiment from this list ONLY:
   [ "Furious", "Frustrated", "Urgent", "Sad", "Confused", "Neutral", "Happy", "Grateful", "Sarcastic", "Professional" ]

Schema:
{
  "summary": "Max 5 words",
  "category": "hardware" | "software" | "network" | "database",
  "priority": "high" | "medium" | "low",
  "sentiment": "One value from the list above",
  "suggested_steps": ["Step 1", "Step 2", "Step 3"]
}
"""

def extract_json(text: str) -> str:
    try:
        match = re.search(r'(\{.*\})', text, re.DOTALL)
        return match.group(1) if match else text
    except: return text

async def analyze_ticket_with_llm(subject: str, description: str) -> TicketAnalysis:
    """ Calls the AI model to classify the ticket. """
    full_text = f"Subject: {subject}\nDescription: {description}"
    
    try:
        response = await aclient.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": full_text}
            ],
            temperature=0.2, # Slightly increased for better nuance detection
            max_tokens=150
        )
        content = extract_json(response.choices[0].message.content)
        return TicketAnalysis.model_validate_json(content)
    except Exception:
        return TicketAnalysis(
            summary="Manual Review",
            category="software",
            priority="medium",
            sentiment="Neutral",
            suggested_steps=["Check logs", "Contact user"]
        )

async def get_next_admin_index(category_name: str, pool_size: int) -> int:
    if pool_size == 0: return 0
    try:
        count = await redis_client.incr(f"ticket_rr:{category_name}")
        return count % pool_size
    except Exception as e:
        try:
            print(f"Redis Error: {e}")
        except UnicodeEncodeError:
            print("Redis Error (non-ASCII chars stripped)")
        return 0