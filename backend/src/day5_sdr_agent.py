import logging
import json
import os
import sys
import asyncio
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

env_path = os.path.join(os.path.dirname(__file__), "../.env.local")
load_dotenv(env_path)

if not os.getenv("GOOGLE_API_KEY"):
    logger = logging.getLogger("day5-sdr-agent")
    logger.error("GOOGLE_API_KEY not found in environment variables!")
    # Try loading from standard .env as fallback
    load_dotenv()

if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("GOOGLE_API_KEY is not set. Please check your .env.local file.")





logger = logging.getLogger("day5-sdr-agent")
logger.setLevel(logging.INFO)
fh = logging.FileHandler("agent_debug.log")
fh.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

# Load Company Info
COMPANY_INFO_PATH = os.path.join(os.path.dirname(__file__), "../day5_company_info.json")
LEADS_FILE_PATH = os.path.join(os.path.dirname(__file__), "../day5_leads.json")

try:
    with open(COMPANY_INFO_PATH, "r") as f:
        COMPANY_DATA = json.load(f)
except FileNotFoundError:
    logger.error(f"Company info file not found at {COMPANY_INFO_PATH}")
    COMPANY_DATA = {"company": "Unknown", "faqs": [], "pricing": {}}

class SDRAgent(Agent):
    def __init__(self):
        company_name = COMPANY_DATA.get("company", "Murf.ai")
        super().__init__(
            instructions=(
                f"You are a friendly and helpful Sales Development Representative (SDR) for {company_name}. "
                f"Your goal is to answer questions about {company_name} using the provided tools and to collect lead information from the user naturally. "
                "Do not be pushy. Be helpful and polite. "
                "You should ask for the following information during the conversation if it hasn't been provided: "
                "Name, Email, Role, Company, Use Case, and Timeline. "
                "Don't ask for everything at once. Mix it into the conversation. "
                "If the user asks a question you don't know, admit it politely and offer to follow up. "
                "When the user says they are done or goodbye, use the end_call_summary tool to give a verbal summary."
            )
        )
        self.lead_info = {}

    @function_tool
    def answer_faq(
        self,
        context: RunContext,
        query: str
    ) -> str:
        """
        Answer questions about the company, pricing, or FAQs using the provided knowledge base.
        
        Args:
            query: The user's question or query about the company.
        """
        logger.info(f"Answering FAQ: {query}")
        
        # Simple keyword search for now
        query_lower = query.lower()
        
        # Check pricing
        if "price" in query_lower or "cost" in query_lower or "plan" in query_lower:
            pricing_text = "Here are our pricing plans:\n"
            for plan, details in COMPANY_DATA.get("pricing", {}).items():
                pricing_text += f"- {plan}: {details['price']}. Features: {', '.join(details['features'][:2])}...\n"
            return pricing_text

        # Check FAQs
        for faq in COMPANY_DATA.get("faqs", []):
            if any(word in query_lower for word in faq["question"].lower().split() if len(word) > 4):
                 return faq["answer"]
        
        # Fallback to general description
        if "what" in query_lower and "do" in query_lower:
             return COMPANY_DATA.get("description", "I can help you with information about Murf.ai.")

        return "I'm not sure about that specific detail, but I can tell you that " + COMPANY_DATA.get("description", "")

    @function_tool
    def capture_lead_info(
        self,
        context: RunContext,
        name: Optional[str] = None,
        email: Optional[str] = None,
        role: Optional[str] = None,
        company: Optional[str] = None,
        use_case: Optional[str] = None,
        timeline: Optional[str] = None,
    ) -> str:
        """
        Capture lead information provided by the user.
        
        Args:
            name: The name of the user.
            email: The email address of the user.
            role: The job role of the user.
            company: The company the user works for.
            use_case: What the user wants to use the product for.
            timeline: When the user plans to start using the product (e.g., now, soon, later).
        """
        logger.info(f"Capturing lead info: {name}, {email}, {role}, {company}, {use_case}, {timeline}")
        
        if name: self.lead_info["name"] = name
        if email: self.lead_info["email"] = email
        if role: self.lead_info["role"] = role
        if company: self.lead_info["company"] = company
        if use_case: self.lead_info["use_case"] = use_case
        if timeline: self.lead_info["timeline"] = timeline

        # Save to file immediately
        self._save_lead()
        
        return "Thanks, I've noted that down."

    def _save_lead(self):
        try:
            leads = []
            if os.path.exists(LEADS_FILE_PATH):
                with open(LEADS_FILE_PATH, "r") as f:
                    try:
                        leads = json.load(f)
                    except json.JSONDecodeError:
                        leads = []
            
            leads.append(self.lead_info)
            
            with open(LEADS_FILE_PATH, "w") as f:
                json.dump(leads, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save lead info: {e}")

    @function_tool
    def end_call_summary(self, context: RunContext) -> str:
        """
        Generates a summary of the call and the lead.
        """
        summary = "Summary of the call:\n"
        summary += f"Lead Name: {self.lead_info.get('name', 'Not provided')}\n"
        summary += f"Role: {self.lead_info.get('role', 'Not provided')}\n"
import logging
import json
import os
import sys
import asyncio
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

load_dotenv(".env.local")





logger = logging.getLogger("day5-sdr-agent")
logger.setLevel(logging.INFO)
fh = logging.FileHandler("agent_debug.log")
fh.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

# Load Company Info
COMPANY_INFO_PATH = os.path.join(os.path.dirname(__file__), "../day5_company_info.json")
LEADS_FILE_PATH = os.path.join(os.path.dirname(__file__), "../day5_leads.json")

try:
    with open(COMPANY_INFO_PATH, "r") as f:
        COMPANY_DATA = json.load(f)
except FileNotFoundError:
    logger.error(f"Company info file not found at {COMPANY_INFO_PATH}")
    COMPANY_DATA = {"company": "Unknown", "faqs": [], "pricing": {}}

class SDRAgent(Agent):
    def __init__(self):
        company_name = COMPANY_DATA.get("company", "Murf.ai")
        super().__init__(
            instructions=(
                f"You are a friendly and helpful Sales Development Representative (SDR) for {company_name}. "
                f"Your goal is to answer questions about {company_name} using the provided tools and to collect lead information from the user naturally. "
                "Do not be pushy. Be helpful and polite. "
                "You should ask for the following information during the conversation if it hasn't been provided: "
                "Name, Email, Role, Company, Use Case, and Timeline. "
                "Don't ask for everything at once. Mix it into the conversation. "
                "If the user asks a question you don't know, admit it politely and offer to follow up. "
                "When the user says they are done or goodbye, use the end_call_summary tool to give a verbal summary."
            )
        )
        self.lead_info = {}

    @function_tool
    def answer_faq(
        self,
        context: RunContext,
        query: str
    ) -> str:
        """
        Answer questions about the company, pricing, or FAQs using the provided knowledge base.
        
        Args:
            query: The user's question or query about the company.
        """
        logger.info(f"Answering FAQ: {query}")
        
        # Simple keyword search for now
        query_lower = query.lower()
        
        # Check pricing
        if "price" in query_lower or "cost" in query_lower or "plan" in query_lower:
            pricing_text = "Here are our pricing plans:\n"
            for plan, details in COMPANY_DATA.get("pricing", {}).items():
                pricing_text += f"- {plan}: {details['price']}. Features: {', '.join(details['features'][:2])}...\n"
            return pricing_text

        # Check FAQs
        for faq in COMPANY_DATA.get("faqs", []):
            if any(word in query_lower for word in faq["question"].lower().split() if len(word) > 4):
                 return faq["answer"]
        
        # Fallback to general description
        if "what" in query_lower and "do" in query_lower:
             return COMPANY_DATA.get("description", "I can help you with information about Murf.ai.")

        return "I'm not sure about that specific detail, but I can tell you that " + COMPANY_DATA.get("description", "")

    @function_tool
    def capture_lead_info(
        self,
        context: RunContext,
        name: Optional[str] = None,
        email: Optional[str] = None,
        role: Optional[str] = None,
        company: Optional[str] = None,
        use_case: Optional[str] = None,
        timeline: Optional[str] = None,
    ) -> str:
        """
        Capture lead information provided by the user.
        
        Args:
            name: The name of the user.
            email: The email address of the user.
            role: The job role of the user.
            company: The company the user works for.
            use_case: What the user wants to use the product for.
            timeline: When the user plans to start using the product (e.g., now, soon, later).
        """
        logger.info(f"Capturing lead info: {name}, {email}, {role}, {company}, {use_case}, {timeline}")
        
        if name: self.lead_info["name"] = name
        if email: self.lead_info["email"] = email
        if role: self.lead_info["role"] = role
        if company: self.lead_info["company"] = company
        if use_case: self.lead_info["use_case"] = use_case
        if timeline: self.lead_info["timeline"] = timeline

        # Save to file immediately
        self._save_lead()
        
        return "Thanks, I've noted that down."

    def _save_lead(self):
        try:
            leads = []
            if os.path.exists(LEADS_FILE_PATH):
                with open(LEADS_FILE_PATH, "r") as f:
                    try:
                        leads = json.load(f)
                    except json.JSONDecodeError:
                        leads = []
            
            leads.append(self.lead_info)
            
            with open(LEADS_FILE_PATH, "w") as f:
                json.dump(leads, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save lead info: {e}")

    @function_tool
    def end_call_summary(self, context: RunContext) -> str:
        """
        Generates a summary of the call and the lead.
        """
        summary = "Summary of the call:\n"
        summary += f"Lead Name: {self.lead_info.get('name', 'Not provided')}\n"
        summary += f"Role: {self.lead_info.get('role', 'Not provided')}\n"
        summary += f"Interest: {self.lead_info.get('use_case', 'General inquiry')}\n"
        summary += f"Timeline: {self.lead_info.get('timeline', 'Unknown')}\n"
        
        return summary

def prewarm(proc: JobProcess):
    try:
        proc.userdata["vad"] = silero.VAD.load()
    except Exception as e:
        logger.error(f"Error in prewarm: {e}", exc_info=True)

async def entrypoint(ctx: JobContext):
    try:
        logger.info(f"connecting to room {ctx.room.name}")
        
        # Initialize turn detector with graceful fallback (HF downloads may fail)
        try:
            turn_model = MultilingualModel()
        except Exception as e:
            logger.warning(f"Turn detector init failed, continuing without it: {e}")
            turn_model = None

        session = AgentSession(
            stt=deepgram.STT(model="nova-3"),
            llm=google.LLM(
                model="gemini-2.5-flash",
                api_key=os.getenv("GOOGLE_API_KEY")
            ), 
            tts=murf.TTS(
                voice="en-US-matthew",
                style="Conversation",
                tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
                text_pacing=True
            ),
            vad=ctx.proc.userdata["vad"],
            turn_detection=turn_model,
        )
        
        @session.on("metrics_collected")
        def _on_metrics_collected(ev: MetricsCollectedEvent):
            metrics.log_metrics(ev.metrics)

        agent = SDRAgent()
        await session.start(agent=agent, room=ctx.room)
        
        await ctx.connect()
        
        company_name = COMPANY_DATA.get("company", "Murf.ai")
        await session.say(f"Hi there! Welcome to {company_name}. I'm your virtual assistant. What brings you here today?", allow_interruptions=True)
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
        # Also write to a separate panic file just in case logger fails
        with open("panic.log", "w") as f:
            f.write(f"Critical error: {e}")
