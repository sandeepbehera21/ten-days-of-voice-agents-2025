import os
import sys
from dotenv import load_dotenv
from livekit.plugins import google, deepgram, murf
from livekit.agents import tokenize

load_dotenv(".env.local")

print("Testing component instantiation...")

try:
    print("Initializing Deepgram STT...")
    stt = deepgram.STT()
    print("Deepgram STT initialized.")
except Exception as e:
    print(f"Failed to initialize Deepgram STT: {e}")

try:
    print("Initializing Google LLM...")
    llm = google.LLM(model="gemini-1.5-flash")
    print("Google LLM initialized.")
except Exception as e:
    print(f"Failed to initialize Google LLM: {e}")

try:
    print("Initializing Murf TTS...")
    tts = murf.TTS(
        voice="en-US-matthew",
        style="Conversation",
        tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
    )
    print("Murf TTS initialized.")
except Exception as e:
    print(f"Failed to initialize Murf TTS: {e}")

    print("Murf TTS initialized.")
except Exception as e:
    print(f"Failed to initialize Murf TTS: {e}")

try:
    from livekit.plugins import silero
    print("Loading Silero VAD...")
    vad = silero.VAD.load()
    print("Silero VAD loaded.")
except Exception as e:
    print(f"Failed to load Silero VAD: {e}")

try:
    from livekit.plugins.turn_detector.multilingual import MultilingualModel
    print("Initializing MultilingualModel...")
    td = MultilingualModel()
    print("MultilingualModel initialized.")
except Exception as e:
    print(f"Failed to initialize MultilingualModel: {e}")

print("Component test complete.")
