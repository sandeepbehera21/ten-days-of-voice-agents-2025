import logging
import os
import sys
import asyncio
import sqlite3
from typing import Annotated, Optional

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
    llm,
    function_tool,
    RunContext,
    metrics,
    MetricsCollectedEvent,
    tokenize
)
from livekit.plugins import google, deepgram, silero, murf
from livekit.plugins.turn_detector.multilingual import MultilingualModel

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), "../.env.local")
load_dotenv(env_path)

if not os.getenv("GOOGLE_API_KEY"):
    load_dotenv() # Fallback

if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("GOOGLE_API_KEY is not set.")

# Configure Logging
logger = logging.getLogger("day6-fraud-agent")
logger.setLevel(logging.INFO)
fh = logging.FileHandler("day6_agent_debug.log")
fh.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

DB_FILE = os.path.join(os.path.dirname(__file__), "../fraud_cases.db")

class FraudAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions=(
                "You are a professional and reassuring Fraud Detection Representative for 'Secure Bank'. "
                "Your goal is to verify a suspicious transaction with the customer. "
                "1. Ask for the customer's name to look up their file. "
                "2. Once identified, verify them by asking their security question. "
                "3. If verified, read out the suspicious transaction details (Merchant, Amount, Time, Location). "
                "4. Ask if they made this transaction. "
                "5. If YES: Mark as safe, thank them, and end call. "
                "6. If NO: Mark as fraud, explain that the card is blocked and a dispute is raised, then end call. "
                "7. If verification fails: Apologize and say you cannot proceed, then end call. "
                "Do NOT ask for full card numbers, PINs, or passwords. "
                "Use the provided tools to look up cases and update status."
            )
        )
        self.current_case = None

    @function_tool
    async def get_fraud_case(self, context: RunContext, user_name: str) -> str:
        """
        Look up a fraud case by user name.
        Args:
            user_name: The name of the customer.
        """
        logger.info(f"Looking up case for: {user_name}")
        try:
            # Run blocking DB operation in executor to avoid blocking the event loop
            loop = asyncio.get_running_loop()
            
            def _query_db():
                conn = sqlite3.connect(DB_FILE)
                conn.row_factory = sqlite3.Row
                c = conn.cursor()
                c.execute("SELECT * FROM fraud_cases WHERE user_name LIKE ?", (f"%{user_name}%",))
                row = c.fetchone()
                conn.close()
                return row

            row = await loop.run_in_executor(None, _query_db)

            if row:
                self.current_case = dict(row)
                return (
                    f"Found case for {self.current_case['user_name']}. "
                    f"Security Question: {self.current_case['security_question']}. "
                    f"Expected Answer: {self.current_case['security_answer']}. "
                    f"Transaction: {self.current_case['merchant']}, {self.current_case['amount']}, "
                    f"at {self.current_case['location']} on {self.current_case['timestamp']}."
                )
            else:
                return "No case found for that name. Please ask the user to repeat their name."
        except Exception as e:
            logger.error(f"Error looking up case: {e}")
            return "There was a system error looking up the case."

    @function_tool
    async def verify_security_answer(self, context: RunContext, user_answer: str) -> str:
        """
        Verify the user's answer to the security question.
        Args:
            user_answer: The answer provided by the user.
        """
        if not self.current_case:
            return "No case loaded. Please ask for the name first."
        
        expected = self.current_case['security_answer'].lower()
        provided = user_answer.lower()
        
        if expected in provided or provided in expected:
            return "Verification successful. Proceed to discuss the transaction."
        else:
            return "Verification failed. The answer does not match our records."

    @function_tool
    async def update_case_status(self, context: RunContext, status: str, notes: str) -> str:
        """
        Update the status of the fraud case in the database.
        Args:
            status: The new status (e.g., 'confirmed_safe', 'confirmed_fraud', 'verification_failed').
            notes: A short note about the outcome.
        """
        if not self.current_case:
            return "No case loaded."
            
        logger.info(f"Updating case {self.current_case['id']} to {status}: {notes}")
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("UPDATE fraud_cases SET status = ? WHERE id = ?", (status, self.current_case['id']))
            conn.commit()
            conn.close()
            return f"Case updated to {status}. You can now end the call."
        except Exception as e:
            logger.error(f"Error updating case: {e}")
            return "Failed to update case status."

def prewarm(proc: JobProcess):
    try:
        proc.userdata["vad"] = silero.VAD.load()
    except Exception as e:
        logger.error(f"Error in prewarm: {e}", exc_info=True)

async def entrypoint(ctx: JobContext):
    try:
        logger.info(f"Connecting to room {ctx.room.name}")
        
        try:
            turn_model = MultilingualModel()
        except Exception as e:
            logger.warning(f"Turn detector init failed: {e}")
            turn_model = None

        session = AgentSession(
            stt=deepgram.STT(model="nova-3"),
            llm=google.LLM(
                model="gemini-2.5-flash",
                api_key=os.getenv("GOOGLE_API_KEY")
            ),
            tts=murf.TTS(
                voice="en-US-matthew", # Or another suitable voice
                style="Conversation",
                tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
                text_pacing=True
            ),
            vad=ctx.proc.userdata["vad"],
            turn_detection=turn_model,
        )
        
        agent = FraudAgent()
        await session.start(agent=agent, room=ctx.room)
        
        await ctx.connect()
        
        await session.say("Hello, this is the fraud prevention department at Secure Bank. I'm calling to verify some recent activity on your account. Could you please confirm your name?", allow_interruptions=True)
        
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
