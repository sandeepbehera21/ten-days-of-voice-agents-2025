# Day 8: Voice Game Master - 3 Minute Video Script

**Goal:** Demonstrate a full D&D-style session with state management, dice rolls, and save/load functionality.

**Tech Stack:**
- **LLM:** Gemini 2.5 Flash
- **TTS:** Murf Falcon (Fastest TTS)
- **Framework:** LiveKit Agents

---

## Script & Timing

### 0:00 - 0:30 | Introduction
**You:**
"Hi everyone! Welcome to Day 8 of the Murf AI Voice Agent Challenge. Today, I've built a **Voice Game Master** that runs an interactive D&D adventure."

"This isn't just a chatbot—it maintains a persistent world state, tracks my inventory, rolls dice for combat, and even lets me save my game. I'm using **Murf Falcon** for the voice, which is incredibly fast and immersive. Let's dive in!"

*(Switch view to the Agent Playground)*

### 0:30 - 1:00 | Starting the Adventure
*(Connect to the agent)*

**Agent:**
"Welcome, traveler. You stand at a dusty crossroads. To the north lies the Dark Forest, to the east the Village of Oakhaven. You have a map, a dagger, and some water. What is your first move?"

**You:**
"I want to check my gear before I head out. What am I carrying?"

**Agent:**
"You currently have: Old Map, Rusty Dagger, Water Skin."

**You:**
"Okay, I'm feeling brave. I'll head North towards the Dark Forest."

### 1:00 - 1:45 | The Encounter (Dice Roll)
**Agent:**
"You step into the Dark Forest. The trees are thick and block out the sun. Suddenly, you hear a low growl from the bushes. A wolf steps out, baring its teeth!"

**You:**
"I'm not backing down. I draw my dagger and try to scare it off!"

**Agent:**
"That's a risky move. I'll need to roll for Intimidation."
*(Agent triggers `roll_dice` tool)*
"Rolled a 14. Success! You shout and wave your dagger. The wolf whimpers and retreats into the shadows."

### 1:45 - 2:30 | Inventory & State Update
**You:**
"Phew, that was close. I look around the area where the wolf was. Is there anything useful?"

**Agent:**
"You search the ground and find a small pouch dropped by a previous traveler. Inside, there is a Healing Potion."

**You:**
"I'll take the Healing Potion."

**Agent:**
*(Agent triggers `add_item` tool)*
"Added Healing Potion to your inventory."

**You:**
"Great. Save my game here, I need to take a break."

**Agent:**
*(Agent triggers `save_game` tool)*
"Game successfully saved to gamestate.json."

### 2:30 - 3:00 | Conclusion
**You:**
"And just like that, I can come back later and say 'Load Game' to pick up exactly where I left off with my potion and stats intact."

"This agent uses a JSON world model to keep track of everything in real-time. It's a powerful way to build interactive stories."

"Thanks for watching Day 8! Don't forget to check out the code, and huge shoutout to Murf AI for the amazing voice tech."

*(Stop Recording)*
