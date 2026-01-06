"""
Phase 4 Solution: LangChain Integration with LCEL Chains
Run with: chainlit run app.py -w
"""

import os
from datetime import date
import chainlit as cl
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnableLambda

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


# Define the prompt template
PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are a helpful AI assistant named Aria. You have the following traits:
- Friendly and conversational tone
- Concise but thorough answers
- You admit when you don't know something
- You can help with coding, writing, analysis, and general questions

Current date: {current_date}
"""
    ),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
])


def create_chain(llm):
    """
    Create a LangChain chain using LCEL (LangChain Expression Language).
    """
    
    def add_current_date(inputs: dict) -> dict:
        """Add the current date to the inputs."""
        inputs["current_date"] = date.today().strftime("%B %d, %Y")
        return inputs
    
    # LCEL chain using the pipe operator
    chain = (
        RunnableLambda(add_current_date)
        | PROMPT_TEMPLATE
        | llm
    )
    
    return chain


@cl.on_chat_start
async def start():
    """Initialize the chat session."""
    llm = get_llm()
    chain = create_chain(llm)
    
    # Store in session
    cl.user_session.set("chain", chain)
    cl.user_session.set("chat_history", [])
    
    await cl.Message(
        content="👋 Hi! I'm Aria, your AI assistant. How can I help you today?"
    ).send()


@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages using the chain."""
    chain = cl.user_session.get("chain")
    chat_history = cl.user_session.get("chat_history")
    
    # Prepare input for the chain
    chain_input = {
        "input": message.content,
        "chat_history": chat_history,
    }
    
    # Stream the response
    msg = cl.Message(content="")
    full_response = ""
    
    async for chunk in chain.astream(chain_input):
        if hasattr(chunk, 'content') and chunk.content:
            full_response += chunk.content
            await msg.stream_token(chunk.content)
    
    await msg.send()
    
    # Update chat history
    chat_history.append(HumanMessage(content=message.content))
    chat_history.append(AIMessage(content=full_response))
    cl.user_session.set("chat_history", chat_history)
