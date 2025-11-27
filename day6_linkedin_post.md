# Day 6 LinkedIn Post Drafts

Here are a few options for your LinkedIn post. Choose the one that fits your style best!

## Option 1: Professional & Impact-Focused (Recommended)

**Headline:** 🛡️ Day 6: Automating Fraud Detection with Voice AI

For Day 6 of the #MurfAIVoiceAgentsChallenge, I built a **Fraud Alert Voice Agent** designed to help banks verify suspicious transactions in real-time.

This agent isn't just a chatbot—it's fully integrated with a backend database. It pulls customer records, verifies identity through security questions, and instantly updates the case status based on the conversation.

**💡 How it works:**
1.  **Detection:** The agent identifies the customer and retrieves their specific fraud case from a SQLite database.
2.  **Verification:** It asks dynamic security questions to confirm identity.
3.  **Action:** Using **Murf Falcon** (the fastest TTS API 🚀), it reads out transaction details clearly and naturally.
4.  **Resolution:** Depending on the user's response, it marks the transaction as "Safe" or "Fraud" directly in the database.

**🛠️ Tech Stack:**
*   **Orchestration:** LiveKit
*   **TTS:** Murf.ai (Falcon)
*   **LLM:** Google Gemini
*   **STT:** Deepgram
*   **Database:** SQLite

Check out the demo below to see the database update in real-time! 👇

#10DaysofAIVoiceAgents #VoiceAI #FraudDetection #FinTech #AI #MurfAI #LiveKit #Python

@Murf AI @ICICI Bank @HDFC Bank @Slice

---

## Option 2: Technical & Developer Centric

**Headline:** ⚡ Real-time Database Integration with Voice Agents

Day 6 of the #MurfAIVoiceAgentsChallenge was all about state management and backend integration. I built a **Fraud Alert Agent** that reads and writes to a local database during a live call.

**The Challenge:**
Create an agent that can handle sensitive context (fraud cases) and persist data changes (marking cases as safe/fraud) without breaking the conversational flow.

**The Solution:**
I used **LiveKit** for the transport and **Murf Falcon** for ultra-low latency speech generation. The agent queries a SQLite database for the user's "security identifier" and "transaction history" and updates the row status immediately after the user confirms the activity.

**Key Features:**
*   ✅ Async database lookups
*   ✅ Dynamic prompt generation based on DB records
*   ✅ Zero-latency voice responses with Murf Falcon

Code is getting more complex, but the results are worth it!

#10DaysofAIVoiceAgents #Coding #Python #VoiceAgent #DevLife #MurfAI

@Murf AI

---

## Option 3: Short & Sweet

**Headline:** Day 6: Keeping your bank account safe with AI! 🏦

Just finished Day 6 of the #MurfAIVoiceAgentsChallenge! Today I built a **Fraud Prevention Voice Agent**.

It calls you up, verifies who you are, and checks if that recent expensive transaction was actually you. 💸

I used **Murf Falcon** for the voice—it's incredibly fast and sounds just like a real bank representative. The coolest part? It updates the bank's database in real-time as we speak.

Watch the demo! 🎥

#10DaysofAIVoiceAgents #MurfAI #FinTech #AI #VoiceTech

@Murf AI
