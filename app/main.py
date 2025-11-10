from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, Any, Dict

from riot import get_yearly_mf_stats
from utils import make_drills
from persona import mf_voice_adapter
from bedrock_ai import mf_bedrock_summary

import base64
from fastapi.responses import JSONResponse
from utils import speak_polly

app = FastAPI(title="Rift Rewind — Miss Fortune Coach")

@app.get("/ping")
def ping():
    return {"status": "ok"}

@app.get("/health")
def health():
    return {"ok": True, "service": "mfcoach", "version": "v1"}

class CoachRequest(BaseModel):
    game_name: str
    tag_line: str

class CoachResponse(BaseModel):
    key_takeaways: list[str]
    drill_next: list[str]
    celebration: str
    roast: str
    bedrock_recap: Optional[str] = None
    stats: Optional[Dict[str, Any]] = None

@app.post("/coach")
async def coach(req: CoachRequest):
    try:
        stats = get_yearly_mf_stats(req.game_name, req.tag_line)
    except Exception as e:
        raise HTTPException(status_code=424, detail=f"Failed to fetch Riot stats: {e}")

    if not stats:
        print("⚠️ Using fallback stats for demo mode")
        stats = {"avg_cs10": 7.2, "avg_deaths_pre_mythic": 1.4, "avg_dragon_presence": 64.0}

    avg_cs10 = stats.get("avg_cs10", 0)
    avg_deaths = stats.get("avg_deaths_pre_mythic", 0)
    avg_dragons = stats.get("avg_dragon_presence", 0)

    drills = make_drills(avg_cs10, avg_deaths, avg_dragons)
    report = {
        "key_takeaways": [
            f"Avg CS@10: {avg_cs10:.1f}",
            f"Avg Deaths pre-Mythic: {avg_deaths:.2f}",
            f"Dragon presence: {avg_dragons:.1f}%"
        ],
        "drill_next": drills[:3],
        "celebration": "You kept at it all year, and it shows. Keep that swagger, captain.",
        "roast": "Still got work to do on that dragon presence. You’re supposed to hit your ult, not just make fireworks.",
    }

    recap = None
    try:
        recap = mf_bedrock_summary(stats, report)
    except Exception:
        recap = None

    merged = mf_voice_adapter(report, stats)
    merged["bedrock_recap"] = recap
    merged["stats"] = stats

    return merged


@app.post("/talk")
async def talk(req: dict):
    print("🗣️ Talk endpoint triggered with request:", req)

    user_msg = req.get("message", "").strip().lower()
    print("💬 User message:", user_msg)

    if not user_msg:
        reply_text = "Say something, sugar — I ain’t a mind reader."
    elif "hello" in user_msg or "hey" in user_msg:
        reply_text = "Well, hello there, sugar. Ready to make some noise on the Rift?"
    elif "tilt" in user_msg or "lost" in user_msg:
        reply_text = "Even bounty hunters have bad games, darlin’. Just reload and go again."
    elif "thanks" in user_msg:
        reply_text = "Don’t mention it, sugar. Just don’t make me chase you down for slippin’."
    elif "bye" in user_msg:
        reply_text = "Goodbye, hotshot. I’ll be waitin’ when the Rift calls again."
    # 🎙️ Generate her voice
    try:
        print("🎧 Generating Polly voice...")
        audio_bytes = speak_polly(reply_text)
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        print("✅ Polly voice generated successfully")
    except Exception as e:
        print(f"❌ Polly error: {e}")
        audio_b64 = None

    return JSONResponse({
        "reply": reply_text,
        "audio": audio_b64
    })
