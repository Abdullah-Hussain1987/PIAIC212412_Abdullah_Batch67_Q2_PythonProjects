import os
from dotenv import load_dotenv
load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
gemini_api_model = os.getenv("GEMINI_API_MODEL")
gemini_api_url = os.getenv("GEMINI_API_URL")

if not gemini_api_key:
    print("GEMINI_API_KEY is not set. Please set it in your .env file.")
    exit(1)

if not gemini_api_model:
    print("GEMINI_API_MODEL is not set. Please set it in your .env file.")
    exit(1)

if not gemini_api_url:
    print("GEMINI_API_URL is not set. Please set it in your .env file.")
    exit(1)

class SecretKeys:
    def __init__(self):
        self.gemini_api_key = gemini_api_key
        self.gemini_api_model = gemini_api_model
        self.gemini_api_url = gemini_api_url

