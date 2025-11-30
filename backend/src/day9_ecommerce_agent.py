import logging
import os
import sys
import asyncio
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

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Import the merchant tools
from day9_merchant_tools import list_products, create_order, get_last_order

load_dotenv(dotenv_path=".env.local")

logger = logging.getLogger("day9-ecommerce-agent")

class EcommerceAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions=(
                "You are a helpful shopping assistant for the 'Murf Store'. "
                "Your goal is to help users browse the catalog (mugs, hoodies, t-shirts) and place orders. "
                "Use 'list_products' to see what is available. You can filter by category, price, or color. "
                "When a user wants to buy something, use 'create_order'. "
                "If they ask about their history, use 'get_last_order'. "
                "Be polite, concise, and confirm details before ordering."
            )
        )

    @function_tool
    async def list_catalog(self, context: RunContext, category: str = None, max_price: int = None, color: str = None) -> str:
        """
        List products from the catalog with optional filters.
        Args:
            category: Filter by category (e.g., 'mug', 'hoodie').
            max_price: Filter by maximum price.
            color: Filter by color.
        """
        return list_products(category, max_price, color)

    @function_tool
    async def place_order(self, context: RunContext, product_id: str, quantity: int = 1) -> str:
        """
        Place an order for a product.
        Args:
            product_id: The ID of the product to buy.
            quantity: The number of items to buy (default 1).
        """
        return create_order(product_id, quantity)

    @function_tool
    async def check_last_order(self, context: RunContext) -> str:
        """
        Check the details of the last order placed.
        """
        return get_last_order()

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

async def entrypoint(ctx: JobContext):
    logger.info(f"connecting to room {ctx.room.name}")
    
    try:
        turn_model = MultilingualModel()
    except Exception:
        turn_model = None

    session = AgentSession(
        vad=ctx.proc.userdata["vad"],
        stt=deepgram.STT(),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice="en-US-julie",
            speed=0,
            pitch=0,
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True
        ),
        turn_detection=turn_model,
    )

    agent = EcommerceAgent()
    
    await session.start(agent=agent, room=ctx.room)
    await ctx.connect()

    # Initial greeting
    await session.say("Welcome to the Murf Store! I can help you find cool mugs, hoodies, and t-shirts. What are you looking for today?", allow_interruptions=True)

if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        ),
    )
