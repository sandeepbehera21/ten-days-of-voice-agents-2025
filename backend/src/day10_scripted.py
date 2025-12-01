"""
Day 10: Improv Battle - Scripted Version (No LLM)
Uses working pattern from day8_gamemaster.py
"""

import logging
import os
from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
    tokenize,
    RunContext,
    function_tool,
)
from livekit.plugins import murf, silero, google, deepgram
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("day10-scripted")
logger.setLevel(logging.INFO)

load_dotenv(".env.local")

# Pre-scripted conversation
RESPONSES = [
    "Welcome to Improv Battle! I'm your host. What is your name, contestant?",
    "Fantastic! Great to have you here! Here's how this works: I'll give you a wild scenario, and you have to act it out with pure improvisation. Ready?",
    "Excellent! Here's your first scenario: You're a penguin trying to convince a polar bear that summer is better than winter. Go ahead, show me what you've got!",
    "Ha! That's hilarious! Okay, next scenario: You're a time traveler from the year 3000 explaining smartphones to someone from the 1800s. Action!",
    "Brilliant! Final round: You're a superhero whose only power is making really good sandwiches. Save the day!",
    "That was absolutely amazing! You've got serious improv skills! Thanks for playing Improv Battle! See you next time!"
]

class ImprovHostScripted(Agent):
    def __init__(self):
        self.response_index = 1  # Start at 1 since we say 0 in entrypoint
        
        super().__init__(
            instructions=f"""You are the host of Improv Battle game show.
            
            IMPORTANT: When the user speaks, respond EXACTLY with this:
            {RESPONSES[self.response_index] if self.response_index < len(RESPONSES) else RESPONSES[-1]}
            
            Do not deviate from this script. Just say it exactly as written.
            """
        )
    
    @function_tool
    async def next_response(self, context: RunContext):
        """Get the next scripted response"""
        if self.response_index < len(RESPONSES):
            response = RESPONSES[self.response_index]
            self.response_index += 1
            return response
        return RESPONSES[-1]

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

async def entrypoint(ctx: JobContext):
    try:
        logger.info(f"Connecting to room {ctx.room.name}")
        
        try:
            turn_model = MultilingualModel()
        except Exception as e:
            logger.warning(f"Turn detector init failed: {e}")
            turn_model = None
        
        # Use Gemini + Murf (same as day8)
        session = AgentSession(
            stt=deepgram.STT(model="nova-3"),
            llm=google.LLM(model="gemini-2.5-flash"),
            tts=murf.TTS(
                voice="en-US-matthew",
                style="Promo",
                tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
                text_pacing=True
            ),
            vad=ctx.proc.userdata["vad"],
            turn_detection=turn_model,
        )
        
        agent = ImprovHostScripted()
        await session.start(agent=agent, room=ctx.room)
        
        await ctx.connect()
        
        # Initial greeting
        await session.say(RESPONSES[0], allow_interruptions=True)
        
    except Exception as e:
        logger.error(f"Error in entrypoint: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    try:
        cli.run_app(
            WorkerOptions(
                entrypoint_fnc=entrypoint,
                prewarm_fnc=prewarm,
            ),
        )
    except Exception as e:
        logger.critical(f"Critical error in main: {e}", exc_info=True)
