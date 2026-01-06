"""
Phase 3 Solution: Basic Chainlit Chat with Conversation Memory
Run with: chainlit run app.py -w
"""

import os
import chainlit as cl
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# Load environment variables
load_dotenv()


def get_llm():
    """Create and return the LLM client."""
    return ChatOpenAI(
        model="gpt-4o-mini",
        api_key=os.getenv("GITHUB_TOKEN"),
        base_url="https://models.inference.ai.azure.com",
        temperature=0.7,
        streaming=True,
    )


# System prompt that defines the assistant's behavior
SYSTEM_PROMPT = """You are a helpful AI assistant. You are friendly, concise, and informative.
When you don't know something, you say so honestly."""


@cl.on_chat_start
async def start():
    """Initialize the chat session."""
    # Store the LLM
    cl.user_session.set("llm", get_llm())
    
    # Initialize message history with system prompt
    cl.user_session.set("messages", [
        SystemMessage(content=SYSTEM_PROMPT)
    ])
    
    await cl.Message(
        content="👋 Hello! I'm an AI assistant powered by GitHub Models. I can remember our conversation. How can I help you today?"
    ).send()


@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages with conversation history."""
    llm = cl.user_session.get("llm")
    messages = cl.user_session.get("messages")
    
    # Add the user's message to history
    messages.append(HumanMessage(content=message.content))
    
    # Create streaming message
    msg = cl.Message(content="")
    full_response = ""
    
    # Stream the response with full history
    async for chunk in llm.astream(messages):
        if chunk.content:
            full_response += chunk.content
            await msg.stream_token(chunk.content)
    
    await msg.send()
    
    # Add assistant's response to history
    messages.append(AIMessage(content=full_response))
    cl.user_session.set("messages", messages)
