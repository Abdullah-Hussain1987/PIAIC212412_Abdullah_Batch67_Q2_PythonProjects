import os
from dotenv import load_dotenv
import rich

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
gemini_api_url = os.getenv("GEMINI_API_URL")
gemini_api_model = os.getenv("GEMINI_API_MODEL")

if not gemini_api_key:
    print("API key not defined")
    exit(1)

if not gemini_api_url:
    print("Base URL not defined")
    exit(1)

if not gemini_api_model:
    print("API model not defined")
    exit(1)

class SecretKeys:
    def __init__(self):
        self.gemini_api_key = gemini_api_key
        self.gemini_api_url = gemini_api_url
        self.gemini_api_model = gemini_api_model