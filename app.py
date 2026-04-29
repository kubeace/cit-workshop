
pavan
import logging
import os
import traceback

from anthropic import AsyncAnthropic
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    print(
        "ERROR: ANTHROPIC_API_KEY environment variable is not set. "
        "Run: export ANTHROPIC_API_KEY=your-key"
    )
    raise RuntimeError("ANTHROPIC_API_KEY environment variable is not set")

client = AsyncAnthropic(api_key=api_key)

SYSTEM_PROMPT = """You are the CIT Campus Assistant — a friendly, concise chatbot for Cambridge Institute of Technology, Bengaluru.

Here is the information you know:

HODs:
- ISE: Dr. Preethi S — preethi.ise@cambridge.edu.in — Image Processing, Computer Networks, Cryptography
- CSE: Dr. Shreekanth Mooroor Prabhu — Shreekanth.cse@cambridge.edu.in — AI/ML, Blockchain, Social Networks
- ECE: Dr. Nagesh K.N (also Vice Principal) — hod.ece@cambridge.edu.in — Wireless Comm, Antennas, RADAR
- EEE: Prof. Hema A — hod.eee@cambridge.edu.in
- Mechanical: Dr. Suneel Kumar N Kulkarni — snkulkarni.mech@cambridge.edu.in
- Civil: Dr. Shankar B.S — hod.civil@cambridge.edu.in

Campus:
- Canteen: 8:30 AM to 4:00 PM
- Library: 8:30 AM to 8:00 PM, closed Sundays
- Address: Cambridge Institute of Technology, An Autonomous Institute, K R Pura, Bengaluru - 560036
- Events: None currently scheduled

Personality: Friendly, concise. If asked something not in the data, say "I don't have that info — check with the college office." Never invent facts."""

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


class ChatRequest(BaseModel):
    message: str


@app.get("/")
async def root():
    return FileResponse("static/index.html")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "cit-campus-assistant"}


@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        response = await client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": request.message}],
        )
        return {"response": response.content[0].text}
    except Exception:
        logger.error("Chat endpoint error:\n%s", traceback.format_exc())
        return {"response": "Sorry, I'm having trouble right now. Please try again."}
