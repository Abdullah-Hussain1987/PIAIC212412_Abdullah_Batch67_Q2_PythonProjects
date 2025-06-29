import os
from dotenv import load_dotenv
load_dotenv()
from rich import print

gemini_api_key = os.getenv("GEMINI_API_KEY")
gemini_api_url = os.getenv("GEMINI_API_URL")
gemini_api_model = os.getenv("GEMINI_API_MODEL")
weather_api_url = os.getenv("WEATHER_API_URL")
weather_api_url = os.getenv("WEATHER_API_URL")
news_api_key = os.getenv("NEWS_API_KEY")


openrouter_api_key = os.getenv("OPEN_ROUTER_API_KEY")
openrouter_api_url = os.getenv("OPEN_ROUTER_API_URL")
openrouter_api_model = os.getenv("OPEN_ROUTER_API_MODEL")

meta_api_model = os.getenv("META_API_MODEL")


if not gemini_api_key:
    print("GEMINI_API_KEY is not set. Please set it in your .env file.")
    exit(1)
if not gemini_api_url:
    print("GEMINI_API_URL is not set. Please set it in your .env file.")
    exit(1)
if not gemini_api_model:
    print("GEMINI_API_MODEL is not set. Please set it in your .env file.")
    exit(1)
if not weather_api_url:
    print(
        "[red]Error:[/red] [green]WEATHER_API_URL[/green] is not set in the environment variables."
    )
    exit(1)

weather_api_key = os.getenv("WEATHER_API_KEY")
if not weather_api_key:
    print(
        "[red]Error:[/red] [green]WEATHER_API_KEY[/green] is not set in the environment variables."
    )
    exit(1)
    
class SecretKeys:
    def __init__(self):
        self.gemini_api_key = gemini_api_key
        self.gemini_api_url = gemini_api_url
        self.gemini_api_model = gemini_api_model
        self.weather_api_url = weather_api_url
        self.weather_api_key = weather_api_key
        self.openrouter_api_key = openrouter_api_key
        self.openrouter_api_url = openrouter_api_url
        self.openrouter_api_model = openrouter_api_model
        self.meta_api_model = meta_api_model
        
