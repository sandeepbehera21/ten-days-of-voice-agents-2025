import logging
import os
import json
import random
from typing import List, Dict, Optional
from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
    llm,
    function_tool,
    RunContext,
    tokenize
)
from livekit.plugins import google, deepgram, silero, murf
from livekit.plugins.turn_detector.multilingual import MultilingualModel

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env.local"))

# Configure Logging
logger = logging.getLogger("day10-improv")
logger.setLevel(logging.INFO)

SCENARIOS = [
    "You are a barista who has to tell a customer that their latte is actually a portal to another dimension.",
    "You are a time-travelling tour guide explaining modern smartphones to someone from the 1800s.",
    "You are a restaurant waiter who must calmly tell a customer that their order has escaped the kitchen.",
    "You are a customer trying to return an obviously cursed object to a very skeptical shop owner.",
    "You are a superhero whose only power is making awkward silences even more awkward, trying to stop a bank robbery."
]

class ImprovGame:
    def __init__(self, max_rounds: int = 3):
        self.player_name: Optional[str] = None
        self.current_round: int = 0
        self.max_rounds: int = max_rounds
        self.rounds: List[Dict] = []
        self.phase: str = "intro" # intro, awaiting_improv, reacting, done
        self.current_scenario: Optional[str] = None

    def set_player_name(self, name: str):
        self.player_name = name

    def start_round(self) -> Optional[str]:
        if self.current_round >= self.max_rounds:
            self.phase = "done"
            return None
        
        self.current_round += 1
        self.current_scenario = random.choice(SCENARIOS)
        self.phase = "awaiting_improv"
        return self.current_scenario

    def end_round(self, reaction: str):
        self.rounds.append({
            "round": self.current_round,
            "scenario": self.current_scenario,
            "reaction": reaction
        })
        self.phase = "reacting"

    def get_state(self):
        return {
            "player_name": self.player_name,
            "current_round": self.current_round,
            "max_rounds": self.max_rounds,
            "phase": self.phase,
            "current_scenario": self.current_scenario
        }

class ImprovHost(Agent):
    def __init__(self):
        self.game = ImprovGame()
        super().__init__(
            instructions=self._get_instructions()
        )

    def _get_instructions(self):
        state = self.game.get_state()
        base_instructions = (
            "You are the host of a TV improv show called 'Improv Battle'. "
            "Your style is high-energy, witty, and clear about rules. "
            "Reactions should be realistic: Sometimes amused, sometimes unimpressed, sometimes pleasantly surprised. "
            "Not always supportive; light teasing and honest critique are allowed. "
            "Stay respectful and non-abusive. "
            f"Current Game State: {json.dumps(state)} "
        )

        if state["phase"] == "intro":
            return base_instructions + (
                "IMMEDIATELY greet the user with: 'Welcome to Improv Battle! I'm your host.' "
                "Then ask the player for their name. "
                "Explain the rules: I will give you a scenario, and you have to act it out. "
                "When you are ready, say 'Let's start' or 'Ready'."
            )
        elif state["phase"] == "awaiting_improv":
            return base_instructions + (
                f"The current scenario is: '{state['current_scenario']}'. "
                "Tell the player the scenario clearly and say 'Action!' to start them. "
                "Listen to their performance. When they seem finished or say 'End scene', "
                "use the 'react_to_scene' tool to give feedback and move to the next round."
            )
        elif state["phase"] == "reacting":
            return base_instructions + (
                "You have just reacted to a scene. "
                "If there are more rounds, announce the next one using 'start_next_round'. "
                "If the game is over (current_round >= max_rounds), summarize the player's performance and say goodbye."
            )
        elif state["phase"] == "done":
            return base_instructions + (
                "The game is over. Thank the player for playing Improv Battle. "
                "Give a final summary of their improv skills based on the rounds. "
                "Say goodbye."
            )
        
        return base_instructions

    @function_tool
    async def set_name(self, context: RunContext, name: str) -> str:
        """Set the player's name."""
        self.game.set_player_name(name)
        self.instructions = self._get_instructions()
        return f"Player name set to {name}. Now explain the rules and ask if they are ready."

    @function_tool
    async def start_next_round(self, context: RunContext) -> str:
        """Start the next round of improv."""
        scenario = self.game.start_round()
        self.instructions = self._get_instructions()
        if scenario:
            return f"Starting Round {self.game.current_round}. Scenario: {scenario}"
        else:
            return "Game over. No more rounds."

    @function_tool
    async def react_to_scene(self, context: RunContext, reaction_feedback: str) -> str:
        """Provide feedback on the player's scene and end the current round."""
        self.game.end_round(reaction_feedback)
        self.instructions = self._get_instructions()
        return f"Reaction recorded: {reaction_feedback}. Now move to next round or end game."

async def entrypoint(ctx: JobContext):
    try:
        logger.info(f"Connecting to room {ctx.room.name}")
        
        ctx.log_context_fields = {"room": ctx.room.name}
        
        # Load VAD manually since we disabled prewarm
        vad = silero.VAD.load()
        
        session = AgentSession(
            stt=deepgram.STT(model="nova-3"),
            llm=google.LLM(model="gemini-2.5-flash"),
            tts=murf.TTS(
                voice="en-US-matthew",
                style="Promo",
                tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
                text_pacing=True
            ),
            turn_detection=MultilingualModel(),
            vad=vad,
            preemptive_generation=True,
        )
        
        agent = ImprovHost()
        
        await session.start(agent=agent, room=ctx.room)
        await ctx.connect()
        
        await session.say("Welcome to Improv Battle! I'm your host. What is your name, contestant?", allow_interruptions=True)
        
    except Exception as e:
        logger.error(f"Error in entrypoint: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    # Disable prewarm to avoid startup timeouts
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
