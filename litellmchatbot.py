import chainlit as cl
from agents import(
    Agent,
    set_tracing_disabled,
    Runner,
)
from mysecrets import SecretKeys
from agents.extensions.models.litellm_model import LitellmModel
from typing import cast
import json


@cl.on_chat_start
async def start():
    set_tracing_disabled(True)
    secret_keys = SecretKeys()
    agent = Agent(
        name="assistant",
        instructions="You are a helpful assistant.",
        model=LitellmModel(
            api_key=secret_keys.gemini_api_key,
            model=secret_keys.gemini_api_model,
        ),
    )
    prompt = cl.Message(content="I am a chatbot powered by Litellm. How can I assist you today?")
    await prompt.send()

    cl.user_session.set("history", [])
    cl.user_session.set("agent", agent)

@cl.on_message
async def handle_message(message:cl.Message):
    prompt = cl.Message(content="")
    agent:Agent = cast(Agent, cl.user_session.get("agent"))

    history = cl.user_session.get("history") or []
    history.append({"role": "user", "content": message.content})
    
    try:
        response = Runner.run_sync(starting_agent=agent, input=history)
        prompt.content = response.final_output
        history.append(response.to_input_list)
        await prompt.update()
           
        cl.user_session.set("history", history)
        

    except Exception as e:
        prompt = cl.Message(content=f"An error occurred: {str(e)}")
        await prompt.update()

@cl.on_chat_end
async def end():
    history = cl.user_session.get("history") or []
    with open("chat_history.json", "w") as f:
        json.dump(history, f, indent=2)