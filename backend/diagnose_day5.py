import os
import sys
from dotenv import load_dotenv

print("Loading .env.local...")
load_dotenv(".env.local")

required_vars = ["LIVEKIT_URL", "LIVEKIT_API_KEY", "LIVEKIT_API_SECRET", "DEEPGRAM_API_KEY", "GOOGLE_API_KEY", "MURF_API_KEY"]
missing = []
for var in required_vars:
    val = os.getenv(var)
    if not val:
        missing.append(var)
    else:
        print(f"{var} is set (length {len(val)})")

if missing:
    print(f"ERROR: Missing environment variables: {missing}")
else:
    print("All environment variables present.")

print("\nTesting imports...")
try:
    from livekit.agents import Agent
    print("livekit.agents imported")
except ImportError as e:
    print(f"Failed to import livekit.agents: {e}")

try:
    from livekit.plugins import google
    print("livekit.plugins.google imported")
except ImportError as e:
    print(f"Failed to import livekit.plugins.google: {e}")

try:
    from livekit.plugins import deepgram
    print("livekit.plugins.deepgram imported")
except ImportError as e:
    print(f"Failed to import livekit.plugins.deepgram: {e}")

try:
    from livekit.plugins import murf
    print("livekit.plugins.murf imported")
except ImportError as e:
    print(f"Failed to import livekit.plugins.murf: {e}")

try:
    from livekit.plugins import silero
    print("livekit.plugins.silero imported")
except ImportError as e:
    print(f"Failed to import livekit.plugins.silero: {e}")

print("\nDiagnostic complete.")
