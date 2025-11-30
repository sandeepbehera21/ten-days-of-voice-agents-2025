# Day 9: E-commerce Agent Demo Script 🎬

**Goal**: Demonstrate the Voice Shopping Assistant with Murf TTS and the Merchant Layer.

## Setup
1.  Ensure the agent is running (`uv run python src/day9_ecommerce_agent.py dev`).
2.  Open the [LiveKit Playground](https://agents-playground.livekit.io/).
3.  Connect to the agent.
4.  Have `backend/day9_orders.json` open in VS Code (or be ready to open it) to show the order persistence.

## Script Flow

**1. Intro & Greeting**
*   **Action**: Connect to the agent.
*   **Agent**: "Welcome to the Murf Store! I can help you find cool mugs, hoodies, and t-shirts. What are you looking for today?"
*   **You**: "Hi! I'm looking for a new hoodie. What do you have?"

**2. Product Browsing (Catalog)**
*   **Agent**: (Lists the hoodies from the catalog, e.g., Developer Hoodie, Cozy Grey Hoodie).
*   **You**: "Tell me more about the Developer Hoodie."
*   **Agent**: "It's a comfortable cotton hoodie with a minimal code logo. Price is 2500 INR."

**3. Placing an Order**
*   **You**: "That sounds perfect. I'll buy one Developer Hoodie."
*   **Agent**: (Calls `create_order`) "Great choice! I've placed your order for the Developer Hoodie. Your order ID is [ID]. Total is 2500 INR."

**4. Verification (The "Wow" Factor)**
*   **You**: "Can you remind me what I just bought?"
*   **Agent**: (Calls `get_last_order`) "Your last order was for 1x Developer Hoodie. Total: INR 2500."
*   **You**: "Thanks!"

**5. Showing the Backend (Crucial for the Challenge)**
*   **Action**: Switch to your VS Code window.
*   **Action**: Open `backend/day9_orders.json`.
*   **You (Voiceover)**: "And here we can see the order was successfully persisted to the JSON file on the backend."

**6. Outro**
*   **You**: "This agent uses the Agentic Commerce Protocol concepts with Murf Falcon TTS for super fast responses. Thanks for watching!"
