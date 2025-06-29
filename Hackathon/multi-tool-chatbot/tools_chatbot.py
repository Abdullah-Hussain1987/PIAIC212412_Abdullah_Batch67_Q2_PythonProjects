# PIAIC212412
# Abdullah Hussain

from agents import(
    Agent,
    OpenAIChatCompletionsModel,
    AsyncOpenAI,
    Runner,
    set_tracing_disabled,
    function_tool,
)
from openai.types.responses import ResponseTextDeltaEvent
import chainlit as cl
from my_secrets import SecretKeys
import requests
import json
from typing import cast
from pydantic import BaseModel
from dotenv import load_dotenv
from input_guardrail import travel_guardrail

load_dotenv()


secrets = SecretKeys()

@cl.set_chat_profiles
async def chat_profile():
    return [
        cl.ChatProfile(
            name="GEMINI-2.0-Flash",
            markdown_description="The underlying LLM model is **GEMINI-2.0-Flash**.",
            icon="/public/gemini.svg",
        ),
        cl.ChatProfile(
            name="DeepSeek-v3",
            markdown_description="The underlying LLM model is **DeepSeek-v3**.",
            icon="/public/deepseek.svg",
        ),
        cl.ChatProfile(
            name="META-Llama-4",
            markdown_description="The underlying LLM model is **META-Llama-4**.",
            icon="/public/meta.svg",
        )
    ]
class TravelPlan(BaseModel):
    destination:str
    activities:list[str]
    budget:float
    duration:int


@function_tool("current_weather_tool")
@cl.step(type="Weather Tool")
async def weather_tool(location:str)->str:
    result=requests.get(
        f"{secrets.weather_api_url}/v1/current.json?key={secrets.weather_api_key}&q={location}"
    )
    if result.status_code != 200:
        return f"Error fetching weather data: {result.status_code}"

    data = result.json()
    return f"Current temperature in {location}: {data['current']['temp_c']}°C, {data['current']['condition']['text']}, {data['current']['feelslike_c']}°C, {data['current']['humidity']}%."


@function_tool("travel_advisor_tool")
@cl.step(type="advisor_tool")
async def travel_advisor_tool(query: str) -> str:
    """Secondary agent for general travel advice."""
    advisor = Agent(
        name="travel_advisor",
        instructions="Provide general travel advice based on user query.",
        model=OpenAIChatCompletionsModel(
            openai_client=AsyncOpenAI(
                base_url=secrets.gemini_api_url,
                api_key=secrets.gemini_api_key,
            ), 
        model=secrets.gemini_api_model,
        ),
    )
       
    result = await Runner.run(advisor, input=[{"role": "user", "content": query}])
    return result.output


def validate_input(message:str)->bool:
    if not message or len(message)<3:
        return False
    if len(message)>500:
        return False
    return True

@cl.set_starters
async def starters():
    return [
        cl.Starter(
            label="Get Latest Weather",
            message="Fetch the current weather of location enter by user.",
            icon="/public/weather.svg",
        ),
        cl.Starter(
            label="Plan a Travel",
            message="Plan a travel to the destination entered by user.",
            icon="/public/student.svg",
        ),
        cl.Starter(
            label="Chat with the Bot",
            message="Start a general conversation with the chatbot.",
            icon= "/public/chat.svg",
        ),
    ]


@cl.on_chat_start
async def start():
    set_tracing_disabled(True)
    chat_profile = cl.user_session.get("chat_profile")
    base_url_name = secrets.gemini_api_url if chat_profile == "GEMINI-2.0-Flash" else secrets.openrouter_api_url
    api_key_name = secrets.gemini_api_key if chat_profile == "GEMINI-2.0-Flash" else secrets.openrouter_api_key
    external_client= AsyncOpenAI(
        base_url=base_url_name,
        api_key=api_key_name,
    )
    
    if chat_profile == "GEMINI-2.0-Flash":
        model_name = secrets.gemini_api_model
    elif chat_profile == "DeepSeek-v3":
        model_name = secrets.openrouter_api_model
    elif chat_profile == "META-Llama-4":
        model_name = secrets.meta_api_model
    else:
        model_name = secrets.gemini_api_model

    
    agent = Agent(
        name="chatbot",
        instructions="""
        * You are a helpful chatbot.
        * For travel planning, create a structured TravelPlan.
        * For weather queries, use weather_tool.
        * For general travel advice, use travel_advisor_tool.
        * Use tools only when necessary.
        * If unsure, ask for clarification.
        """,
        model=OpenAIChatCompletionsModel(
            openai_client=external_client,
            model=model_name,
        ),
        tools=[
            weather_tool, 
            
            travel_advisor_tool,
        ],
        input_guardrails=[travel_guardrail],
        

    )
    cl.user_session.set("agent", agent)
    cl.user_session.set("chat_history", [])
    

@cl.on_message
async def main(message: cl.Message):
    if not validate_input(message.content):
        await cl.Message(content="Invalid input. Please enter a message between 5 and 500 characters.").send()
        return
    
    thinking_msg=cl.Message(content="Thinking...")
    await thinking_msg.send()

    agent=cast(Agent,cl.user_session.get("agent"))
    chat_history:list=cl.user_session.get("chat_history") or []
    chat_history.append(
        {
            "role": "user",
            "content": message.content,
        }
    )

    try:
        if "plan a trip" in message.content.lower():
            result = Runner.run_streamed(
                starting_agent=agent,
                input=chat_history,
            )
        else:
            result = Runner.run_streamed(
                starting_agent=agent,
                input=[{"role": "user", "content": f"use travel_advisor_tool: {message.content}"}],
            )
        result = Runner.run_streamed(
            starting_agent=agent,
            input=chat_history,
        )
        response_message = cl.Message(
            content="",            
        )
        first_response = True
        async for chunk in result.stream_events():
            if chunk.type == "raw_response_event" and isinstance(chunk.data, ResponseTextDeltaEvent):
                if first_response:
                    await thinking_msg.remove()
                    await response_message.send()
                    first_response = False
                await response_message.stream_token(chunk.data.delta)
       
                
            chat_history.append(
            {
                "role": "assistant",
                "content": response_message.content,
            }
        )
        cl.user_session.set("chat_history", chat_history)
        await response_message.update()
    except Exception as e:
        response_message.content = f"An error occurred: {str(e)}"
        await response_message.update()


@cl.on_chat_end
def end():
    chat_history = cl.user_session.get("chat_history") or []
    with open("chat_history.json", "w") as f:
        json.dump(chat_history, f, indent=4)

