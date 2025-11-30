import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv(".env.local")

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ GOOGLE_API_KEY not found in .env.local")
else:
    print(f"✅ Found GOOGLE_API_KEY: {api_key[:5]}...{api_key[-5:]}")
    
    genai.configure(api_key=api_key)
    
    models_to_try = ['gemini-2.5-flash', 'gemini-1.5-flash']
    
    for model_name in models_to_try:
        print(f"\nTesting model: {model_name}...")
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Hello")
            print(f"✅ SUCCESS with {model_name}! Response: {response.text}")
            break
        except Exception as e:
            print(f"❌ FAILED with {model_name}: {e}")
