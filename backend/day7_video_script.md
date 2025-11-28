# Day 7 Video Script: Grocery Ordering Agent

**Intro:**
"Hi everyone! This is Day 7 of the Murf AI Voice Agent Challenge. Today, I built a Food & Grocery Ordering Voice Agent using Murf Falcon for TTS and Gemini 2.0 Flash for intelligence. Let's see it in action!"

**Step 1: Start the Conversation**
*   **You:** "Hi there!"
*   **Agent:** "Welcome to FreshMart! I can help you order groceries or find ingredients for your next meal. What can I get for you today?"

**Step 2: Add Specific Items**
*   **You:** "I need a gallon of whole milk and a dozen eggs."
*   **Agent:** (Should confirm adding milk and eggs to the cart)

**Step 3: Test "Ingredients for X" Logic**
*   **You:** "I also want to make a peanut butter sandwich. What do I need for that?"
*   **Agent:** (Should suggest bread and peanut butter) "You'll need Whole Wheat Bread and Peanut Butter. Shall I add those to your cart?"
*   **You:** "Yes, please add them."

**Step 4: Check Cart**
*   **You:** "Great. What do I have in my cart so far?"
*   **Agent:** (Lists milk, eggs, bread, peanut butter and the total)

**Step 5: Place Order**
*   **You:** "That looks good. Place the order."
*   **Agent:** (Confirms order placement and gives an Order ID)

**Step 6: Track Order**
*   **You:** "Where is my order?"
*   **Agent:** (Should say the status is 'received')

**Outro:**
"And that's it! The order is saved to a JSON file in the backend, and the agent can track its status. Thanks for watching!"
