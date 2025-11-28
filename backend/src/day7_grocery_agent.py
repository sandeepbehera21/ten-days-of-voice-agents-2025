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
from livekit.plugins import openai, deepgram, silero, google, murf
from livekit.plugins.turn_detector.multilingual import MultilingualModel

from grocery_tools import GroceryCart, OrderManager

load_dotenv(os.path.join(os.path.dirname(__file__), "../.env.local"))

logger = logging.getLogger("grocery-agent")

class GroceryAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions=(
                "You are a friendly and helpful grocery shopping assistant for 'FreshMart'. "
                "Your goal is to help users browse the catalog, add items to their cart, and place orders. "
                "You can also help users find ingredients for specific dishes. "
                "If a user asks for ingredients for a dish (e.g., 'ingredients for a sandwich'), "
                "suggest the necessary items from the catalog and offer to add them to the cart. "
                "Always confirm the quantity and item name before adding to the cart if it's ambiguous. "
                "When the user is ready, help them place the order. "
                "You also have access to order tracking. "
                "Be concise and polite."
            )
        )
        self.cart = GroceryCart()
        self.order_manager = OrderManager()

    @function_tool
    async def add_to_cart(self, context: RunContext, item_name: str, quantity: int = 1) -> str:
        """
        Add an item to the shopping cart.
        Args:
            item_name: The name of the item to add.
            quantity: The number of items to add (default 1).
        """
        return self.cart.add_item(item_name, quantity)

    @function_tool
    async def remove_from_cart(self, context: RunContext, item_name: str) -> str:
        """
        Remove an item from the shopping cart.
        Args:
            item_name: The name of the item to remove.
        """
        return self.cart.remove_item(item_name)

    @function_tool
    async def get_cart(self, context: RunContext) -> str:
        """
        Get the current contents of the shopping cart.
        """
        return self.cart.get_cart_details()

    @function_tool
    async def place_order(self, context: RunContext) -> str:
        """
        Place the order with the current cart contents.
        """
        return self.order_manager.place_order(self.cart)

    @function_tool
    async def track_order(self, context: RunContext, order_id: str = None) -> str:
        """
        Track an order by ID or get the status of the latest order.
        Args:
            order_id: The ID of the order to track (optional).
        """
        return self.order_manager.get_order_status(order_id)

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
        llm=google.LLM(model="gemini-2.0-flash"),
        tts=murf.TTS(
            voice="en-US-marcus",
            speed=0,
            pitch=0,
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True
        ),
        turn_detection=turn_model,
    )

    agent = GroceryAgent()
    
    await session.start(agent=agent, room=ctx.room)
    await ctx.connect()
    
    await session.say("Welcome to FreshMart! I can help you order groceries or find ingredients for your next meal. What can I get for you today?", allow_interruptions=True)

if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        ),
    )
