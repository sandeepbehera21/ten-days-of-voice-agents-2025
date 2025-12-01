"""
Day 10: Improv Battle - Simplified Version
Pre-scripted responses - No LLM, No rate limits!
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
    llm,
)
from livekit.plugins import deepgram, silero

logger = logging.getLogger("day10-simple")
logger.setLevel(logging.INFO)

load_dotenv(".env.local")

# Pre-scripted responses
SCRIPT = [
    "Welcome to Improv Battle! I'm your host. What is your name, contestant?",
    "Fantastic! Great to have you here! Here's how this works: I'll give you a wild scenario, and you have to act it out with pure improvisation. Ready?",
    "Excellent! Here's your first scenario: You're a penguin trying to convince a polar bear that summer is better than winter. Go ahead, show me what you've got!",
    "Ha! That's hilarious! Okay, next scenario: You're a time traveler from the year 3000 explaining smartphones to someone from the 1800s. Action!",
    "Brilliant! Final round: You're a superhero whose only power is making really good sandwiches. Save the day!",
    "That was absolutely amazing! You've got serious improv skills! Thanks for playing Improv Battle! See you next time!"
]

class SimpleLLM(llm.LLM):
    """Scripted LLM - no API calls"""
    
    def __init__(self):
        self.response_index = 0
    
    def chat(self, *, chat_ctx: llm.ChatContext, **kwargs) -> llm.LLMStream:
        return SimpleLLMStream(self)

class SimpleLLMStream(llm.LLMStream):
    def __init__(self, llm_instance):
        self._llm = llm_instance
        self._done = False
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        if self._done:
            raise StopAsyncIteration
        
        # Get next response
        if self._llm.response_index < len(SCRIPT):
            response = SCRIPT[self._llm.response_index]
            self._llm.response_index += 1
        else:
            response = "Thanks for playing!"
        
        self._done = True
        
        # Return chunk
        return llm.ChatChunk(
            choices=[
                llm.Choice(
                    delta=llm.ChoiceDelta(
                        role="assistant",
                        content=response
                    )
                )
            ]
        )

class ImprovHost(Agent):
    def __init__(self):
        super().__init__(
            instructions="You are the host of Improv Battle, a fun improv game show."
        )

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

async def entrypoint(ctx: JobContext):
    try:
        logger.info(f"Connecting to room {ctx.room.name}")
        
        # Create session with simple LLM
        session = AgentSession(
            stt=deepgram.STT(model="nova-3"),
            llm=SimpleLLM(),
            tts=deepgram.TTS(model="aura-asteria-en"),
            vad=ctx.proc.userdata["vad"],
        )
        
        agent = ImprovHost()
        
        # Start session
        await session.start(agent=agent, room=ctx.room)
        await ctx.connect()
        
        # Initial greeting
        await session.say(SCRIPT[0], allow_interruptions=True)
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
