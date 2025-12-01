"""
Day 10: Improv Battle - Simplified Version with Pre-scripted Responses
No LLM required - perfect for demo recording
"""

import logging
import os
import asyncio
from dotenv import load_dotenv
from livekit.agents import (
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
    llm,
)
from livekit.plugins import deepgram, silero
from livekit import rtc

logger = logging.getLogger("day10-improv-simple")
logger.setLevel(logging.INFO)

load_dotenv(".env.local")

# Pre-scripted conversation flow
RESPONSES = {
    "intro": "Welcome to Improv Battle! I'm your host. What is your name, contestant?",
    "got_name": "Fantastic! Great to have you here, {name}! Here's how this works: I'll give you a wild scenario, and you have to act it out with pure improvisation. Ready?",
    "scenario_1": "Excellent! Here's your first scenario: You're a penguin trying to convince a polar bear that summer is better than winter. Go ahead, show me what you've got!",
    "scenario_2": "Ha! That's hilarious! Okay, next scenario: You're a time traveler from the year 3000 explaining smartphones to someone from the 1800s. Action!",
    "scenario_3": "Brilliant! Final round: You're a superhero whose only power is making really good sandwiches. Save the day!",
    "ending": "That was absolutely amazing! You've got serious improv skills, {name}! Thanks for playing Improv Battle! See you next time!"
}

class ScriptedLLM(llm.LLM):
    """Fake LLM that returns pre-scripted responses"""
    
    def __init__(self):
        self.turn = 0
        self.user_name = "contestant"
        self.script_order = ["intro", "got_name", "scenario_1", "scenario_2", "scenario_3", "ending"]
    
    def chat(
        self,
        *,
        chat_ctx: llm.ChatContext,
        temperature: float | None = None,
        n: int | None = 1,
    ) -> "llm.LLMStream":
        return ScriptedLLMStream(self, chat_ctx)

class ScriptedLLMStream(llm.LLMStream):
    def __init__(self, llm_instance: ScriptedLLM, chat_ctx: llm.ChatContext):
        self._llm = llm_instance
        self._chat_ctx = chat_ctx
        
    async def __anext__(self) -> llm.ChatChunk:
        # Get the last user message
        user_messages = [msg for msg in self._chat_ctx.messages if msg.role == "user"]
        
        if user_messages:
            last_user_msg = user_messages[-1].content.lower()
            
            # Extract name if mentioned
            if self._llm.turn == 0 and any(word in last_user_msg for word in ["my name is", "i'm", "i am", "call me"]):
                words = last_user_msg.split()
                for i, word in enumerate(words):
                    if word in ["is", "i'm", "am", "me"] and i + 1 < len(words):
                        self._llm.user_name = words[i + 1].strip(".,!?")
                        break
        
        # Get next response
        if self._llm.turn < len(self._llm.script_order):
            key = self._llm.script_order[self._llm.turn]
            response = RESPONSES[key].format(name=self._llm.user_name)
            self._llm.turn += 1
            
            # Return as chunk
            chunk = llm.ChatChunk(
                choices=[
                    llm.Choice(
                        delta=llm.ChoiceDelta(
                            role="assistant",
                            content=response
                        )
                    )
                ]
            )
            
            # Yield the chunk once
            yield chunk
            
        # Stop iteration
        raise StopAsyncIteration

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

async def entrypoint(ctx: JobContext):
    from livekit.agents import AgentSession
    
    try:
        logger.info(f"Connecting to room {ctx.room.name}")
        
        # Create session with scripted LLM
        session = AgentSession(
            stt=deepgram.STT(model="nova-3"),
            llm=ScriptedLLM(),
            tts=deepgram.TTS(model="aura-asteria-en"),
            vad=ctx.proc.userdata["vad"],
        )
        
        # Start session
        await session.start(room=ctx.room)
        await ctx.connect()
        
        # Initial greeting
        await session.say(RESPONSES["intro"], allow_interruptions=True)
        
    except Exception as e:
        logger.error(f"Error in entrypoint: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
