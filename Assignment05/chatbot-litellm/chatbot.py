import chainlit as cl
from secret_keys import SecretKeys
from litellm import acompletion
import json


@cl.on_chat_start
async def start():
   
    cl.user_session.set("chat_history", [])
    msg= cl.Message(content="Welcome to the Chatbot. How may I assist you?")
    await msg.send()

@cl.on_message
async def message_handler(message:cl.Message):
    secrets=SecretKeys()
    msg = cl.Message(content="")
    await msg.send()
    history = cl.user_session.get("chat_history") or []
    history.append({"role":"user","content":message.content})

    try:
        response = await acompletion(
        model="gemini/gemini-1.5-flash",
        api_key= secrets.gemini_api_key,
        messages=history,
        stream = True,
        )
        
        async for chunk in response:
            if token := chunk.choices[0].delta.content or "":
                await msg.stream_token(token)
        await msg.update()
        history.append({"role": "assistant", "content": msg.content})
        cl.user_session.set("chat_history", history)

    except Exception as e:
        msg.content = f"Error: {str(e)}"
        await msg.update()

@cl.on_chat_end
async def on_chat_end():
    history = cl.user_session.get("chat_history") or []
    with open("chat_history.json", "w") as f:
        json.dump(history, f, indent=2)
    
