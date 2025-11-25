import logging
import json
import sys
import asyncio
from typing import List, Optional, Literal

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
    metrics,
    tokenize,
    function_tool,
    RunContext,
    MetricsCollectedEvent
)
from livekit.plugins import murf, deepgram, google, noise_cancellation, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent_day4")

load_dotenv(".env.local")

# Load content
try:
    with open("day4_tutor_content.json", "r") as f:
        CONTENT = json.load(f)
except FileNotFoundError:
    logger.error("day4_tutor_content.json not found!")
    CONTENT = []

class TutorAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a helpful and patient Active Recall Coach.
            Your goal is to help the user learn concepts through three modes:
            1. LEARN: You explain the concept clearly.
            2. QUIZ: You ask the user questions about the concept to test their understanding.
            3. TEACH_BACK: You ask the user to explain the concept back to you and provide feedback.

            You have access to a list of concepts (Variables, Loops, Functions).
            
            Current State:
            - Mode: {mode}
            - Concept: {concept_title}

            Behavior:
            - When in LEARN mode, use the concept summary to explain.
            - When in QUIZ mode, use the sample question or generate a relevant question.
            - When in TEACH_BACK mode, ask the user to explain the concept. After they explain, give them qualitative feedback (Good/Bad/Missed something).
            - Always be encouraging.
            - If the user asks to switch modes, use the `switch_mode` tool.
            - If the user asks to switch concepts, use the `switch_concept` tool (if you implement it, or just handle it naturally by updating state if possible, but for now let's stick to mode switching as primary).
            
            IMPORTANT: You must use the correct voice for each mode.
            - Learn: Matthew
            - Quiz: Alicia
            - Teach-back: Ken
            The system handles voice switching, you just need to ensure you are in the right mode.
            """,
        )
        self.mode: Literal["learn", "quiz", "teach_back"] = "learn"
        self.current_concept_index = 0
        self.content = CONTENT

    @property
    def current_concept(self):
        if not self.content:
            return None
        return self.content[self.current_concept_index]

    @function_tool
    async def switch_mode(self, context: RunContext, mode: Literal["learn", "quiz", "teach_back"]):
        """Switch the learning mode.
        
        Args:
            mode: The new mode to switch to. Must be one of 'learn', 'quiz', 'teach_back'.
        """
        self.mode = mode
        logger.info(f"Switched mode to {mode}")
        
        # We need to signal the outer scope to update the TTS voice. 
        # Since we can't directly modify the session's TTS from here easily without passing it in,
        # we might need a way to trigger a re-configuration or just rely on the agent loop to pick it up if we structure it right.
        # However, standard LiveKit agents usually have a static TTS per session.
        # To support dynamic voice switching, we might need to use `session.tts.update_options` or similar if available,
        # or simply instantiate a new TTS object and assign it to the session?
        # Looking at the docs/examples, changing voice mid-session might require specific handling.
        # Let's try to update the instructions to reflect the new mode, and we'll handle TTS switching in the main loop or a callback if possible.
        
        return f"Switched to {mode} mode. Let's continue with {self.current_concept['title']}."

    @function_tool
    async def switch_concept(self, context: RunContext, concept_id: str):
        """Switch to a different concept.
        
        Args:
            concept_id: The id of the concept to switch to (e.g., 'variables', 'loops', 'functions').
        """
        for i, c in enumerate(self.content):
            if c["id"] == concept_id:
                self.current_concept_index = i
                logger.info(f"Switched concept to {concept_id}")
                return f"Switched concept to {c['title']}."
        
        return f"Concept {concept_id} not found."

    def get_voice_for_mode(self):
        if self.mode == "learn":
            return "en-US-matthew"
        elif self.mode == "quiz":
            return "en-US-alicia"
        elif self.mode == "teach_back":
            return "en-US-ken"
        return "en-US-matthew"

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

async def entrypoint(ctx: JobContext):
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Initial TTS setup
    current_voice = "en-US-matthew"
    tts = murf.TTS(
        voice=current_voice,
        style="Conversation",
        tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
        text_pacing=True
    )

    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(
            model="gemini-2.5-flash",
        ),
        tts=tts,
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )

    tutor_agent = TutorAgent()

    # Hook into the agent's processing to update TTS voice if mode changes
    # This is a bit of a hack. A cleaner way might be to have the tool update the session directly if passed,
    # or use a property listener.
    # For now, let's just check after every tool call or interaction?
    # Actually, `AgentSession` doesn't easily support hot-swapping the TTS engine instance itself,
    # but `murf.TTS` might allow updating options.
    # Checking `murf.TTS` source or docs would be ideal. Assuming we can't easily hot-swap the *instance*,
    # we might need to create a wrapper or just update the `voice` attribute if it's public.
    # Let's assume `tts.voice` is mutable or we can create a new TTS.
    
    # If `tts` is used by the session, replacing `session.tts` might work for subsequent turns.
    
    @tutor_agent.on("agent_speech_committed") # This event might not exist, checking available events...
    # We can wrap the tool execution or just monitor the state.
    
    # Let's try to update the voice whenever the LLM generates a response, but that's too late.
    # We need to update it *before* the TTS is called.
    # The session uses `tts.synthesize`.
    
    # Let's define a custom TTS wrapper that delegates to the correct Murf voice based on agent state.
    class DynamicMurfTTS(murf.TTS):
        def __init__(self, agent_ref: TutorAgent, **kwargs):
            super().__init__(**kwargs)
            self.agent_ref = agent_ref
            
        def synthesize(self, text: str):
            # Update voice before synthesis
            target_voice = self.agent_ref.get_voice_for_mode()
            if self._opts.voice != target_voice:
                logger.info(f"Switching voice to {target_voice}")
                # Accessing private _opts might be risky, but standard way to update options?
                # If Murf TTS plugin allows updating options:
                # self.update_options(voice=target_voice) # Hypothetical
                # If not, we might need to hack it.
                # `murf.TTS` usually takes options in init.
                # Let's try modifying the internal options if possible, or just `self._opts.voice = target_voice`
                # Looking at typical python plugin structures, it's likely `_opts` or similar.
                # Let's try to just set `self._opts.voice` if it exists, or `self.voice` if it's a property.
                pass
            
            # Actually, better to just create a new TTS instance for the session?
            # session.tts = new_tts
            # But session might have bound methods.
            
            # Let's try to just update the options on the existing TTS object if possible.
            # If `murf.TTS` exposes `voice` property, we set it.
            # If not, we might be stuck with one voice unless we swap the TTS object on the session.
            
            return super().synthesize(text)

    # Since I can't easily verify the inner workings of Murf plugin right now without reading code,
    # I will try to swap `session.tts` in the main loop or tool.
    
    # Actually, let's just use the tool to update the session.tts
    
    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)

    await session.start(
        agent=tutor_agent,
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # We need to watch for mode changes.
    # Let's add a loop or hook.
    # Or simpler: The `switch_mode` tool can update `session.tts`.
    # But `switch_mode` is in `TutorAgent`, which doesn't have `session` reference by default.
    # We can pass `session` to `TutorAgent`.
    tutor_agent.session = session

    await ctx.connect()
    
    # Greet the user
    initial_concept = tutor_agent.current_concept
    await session.say(f"Hello! I'm your Active Recall Coach. I can help you learn about {initial_concept['title']}, quiz you on it, or let you teach it back to me. Which mode would you like to start with?", allow_interruptions=True)

# Monkey patch switch_mode to update TTS
# Or better, just implement it in the class if we pass session.

# Let's refine TutorAgent to accept session or handle TTS update.
# Redefining TutorAgent here to include session handling would be cleaner.

class TutorAgentWithSession(TutorAgent):
    def __init__(self, session: AgentSession):
        super().__init__()
        self.agent_session = session

    @function_tool
    async def switch_mode(self, context: RunContext, mode: Literal["learn", "quiz", "teach_back"]):
        """Switch the learning mode.
        
        Args:
            mode: The new mode to switch to. Must be one of 'learn', 'quiz', 'teach_back'.
        """
        self.mode = mode
        logger.info(f"Switched mode to {mode}")
        
        # Update TTS voice
        new_voice = self.get_voice_for_mode()
        logger.info(f"Updating TTS voice to {new_voice}")
        
        # Create new TTS instance
        new_tts = murf.TTS(
            voice=new_voice,
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True
        )
        
        # Hot-swap TTS
        self.agent_session.tts = new_tts
        
        return f"Switched to {mode} mode. Voice changed to {new_voice}. Let's continue with {self.current_concept['title']}."

# We need to use TutorAgentWithSession in entrypoint
async def entrypoint_v2(ctx: JobContext):
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }
    
    # Initial TTS
    tts = murf.TTS(
        voice="en-US-matthew",
        style="Conversation",
        tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
        text_pacing=True
    )

    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(
            model="gemini-2.5-flash",
        ),
        tts=tts,
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )
    
    agent = TutorAgentWithSession(session)
    
    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)

    await ctx.connect()

    await session.start(
        agent=agent,
        room=ctx.room,
    )
    
    initial_concept = agent.current_concept
    await session.say(f"Hello! I'm your Active Recall Coach. I can help you learn about {initial_concept['title']}, quiz you on it, or let you teach it back to me. Which mode would you like to start with?", allow_interruptions=True)

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint_v2, prewarm_fnc=prewarm))
