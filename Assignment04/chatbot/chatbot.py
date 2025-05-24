# PIAIC212412
# Abdullah Hussain

import chainlit as cl
from agents import (
    Agent, 
    Runner, 
    AsyncOpenAI, 
    set_tracing_disabled, 
    OpenAIChatCompletionsModel,
)
from rich import print
from typing import cast
import json
from secret_keys import SecretKeys 

@cl.on_chat_start
async def start():
    set_tracing_disabled(True)
    my_keys = SecretKeys()
    external_client = AsyncOpenAI(
        api_key = my_keys.gemini_api_key,
        base_url = my_keys.gemini_api_url,
    )    
    agent = Agent(
        name="ChatBot",
        instructions = "Answer the user's questions to the best of your ability.",
        model = OpenAIChatCompletionsModel(
            model=my_keys.gemini_api_model,
            openai_client=external_client,
            
        ),
    )
    msg = "Welcome to the ChatBot! I'm here to assist you with your queries. Let's get started!"
    await cl.Message(content=msg).send()
    
    cl.user_session.set("agent", agent) 
    cl.user_session.set("chat_history", [])
    
@cl.on_message
async def main(message: cl.Message):
    
    msg = cl.Message(content="Generating response...")
    await msg.send()

    agent:Agent = cast(Agent, cl.user_session.get("agent"))
    
    chat_history = cl.user_session.get("chat_history") or []
    chat_history.append({"role": "user", "content": message.content})

    try:
        result = Runner.run_sync(starting_agent=agent, input=chat_history)
        msg.content = result.final_output
        await msg.update()
        cl.user_session.set("chat_history", result.to_input_list())

    except Exception as e:
        msg.content = f"An error occurred: {str(e)}"
        await msg.update()
        print(f"Error: {e}")
    

@cl.on_chat_end
async def end():
    chat_history = cl.user_session.get("chat_history") or []
    
    with open("chat_history.json", "w") as f:
        json.dump(chat_history, f, indent=4)
