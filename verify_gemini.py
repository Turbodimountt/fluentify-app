import asyncio
import os
import sys
from dotenv import load_dotenv
load_dotenv("backend/.env")

# Add backend to path to import app modules
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from app.core.config import settings
from app.services.ai_engine import generate_ai_response, build_system_prompt

async def test_gemini():
    print("--- Testing Gemini Integration ---")
    print(f"API Key configured: {'Yes' if settings.google_api_key else 'No'}")
    
    if not settings.google_api_key:
        print("Error: GOOGLE_API_KEY not found in settings. Check your .env file.")
        return

    system_prompt = build_system_prompt(
        mode="libre",
        target_language="English",
        native_language="Spanish",
        cefr_level="B1"
    )
    
    messages = [
        {"role": "user", "content": "Hello! I want to practice my English. Can we talk about technology?"}
    ]
    
    try:
        print("\nSending request to Gemini...")
        response = await generate_ai_response(messages, system_prompt)
        print("\n--- AI Response ---")
        print(response)
        print("\n--- End of Response ---")
        
        if "[CORRECTIONS]" in response:
            print("\nSuccess: Custom tags [CORRECTIONS] found in response.")
        else:
            print("\nWarning: Custom tags [CORRECTIONS] NOT found in response. Gemini might need prompt tuning.")
            
    except Exception as e:
        print(f"\nError during API call: {e}")
        print("\nMake sure 'google-generativeai' is installed: pip install google-generativeai")

if __name__ == "__main__":
    asyncio.run(test_gemini())
