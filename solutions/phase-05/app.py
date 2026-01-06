"""
Phase 5 Solution: Tool-Calling Agent with Weather API
Run with: chainlit run app.py -w
"""

import os
from datetime import date
import chainlit as cl
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain.agents import create_tool_calling_agent, AgentExecutor

from tools import TOOLS

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


# Agent prompt template
AGENT_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are a helpful AI assistant named Aria. You have access to the following tools:

{tools}

Use these tools when appropriate to help answer user questions. For weather queries, 
always use the get_weather tool rather than making up information.

Guidelines:
- Be friendly and conversational
- When using tools, explain what you're doing
- If a tool returns an error, explain the issue to the user
- For non-tool questions, answer directly from your knowledge

Current date: {current_date}
"""
    ),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])


@cl.on_chat_start
async def start():
    """Initialize the chat session with the agent."""
    llm = get_llm()
    
    # Create the agent
    agent = create_tool_calling_agent(llm, TOOLS, AGENT_PROMPT)
    
    # Create the agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=TOOLS,
        verbose=True,
        handle_parsing_errors=True,
    )
    
    # Store in session
    cl.user_session.set("agent_executor", agent_executor)
    cl.user_session.set("chat_history", [])
    
    await cl.Message(
        content="👋 Hi! I'm Aria, your AI assistant. I can now check the weather for you! Try asking: 'What's the weather in Paris?'"
    ).send()


@cl.on_message
async def main(message: cl.Message):
    """Handle messages with the agent."""
    agent_executor = cl.user_session.get("agent_executor")
    chat_history = cl.user_session.get("chat_history")
    
    # Prepare input
    agent_input = {
        "input": message.content,
        "chat_history": chat_history,
        "current_date": date.today().strftime("%B %d, %Y"),
    }
    
    # Create a message for streaming
    msg = cl.Message(content="")
    full_response = ""
    current_step = None
    
    try:
        async for event in agent_executor.astream_events(agent_input, version="v2"):
            kind = event["event"]
            
            if kind == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content:
                    full_response += content
                    await msg.stream_token(content)
                    
            elif kind == "on_tool_start":
                tool_name = event["name"]
                tool_input = event["data"].get("input", {})
                current_step = cl.Step(name=f"🔧 {tool_name}", type="tool")
                current_step.input = str(tool_input)
                await current_step.send()
                
            elif kind == "on_tool_end":
                if current_step:
                    tool_output = event["data"].get("output", "")
                    current_step.output = tool_output
                    await current_step.update()
                    current_step = None
        
        if full_response:
            await msg.send()
        
        # Update chat history
        chat_history.append(HumanMessage(content=message.content))
        chat_history.append(AIMessage(content=full_response))
        cl.user_session.set("chat_history", chat_history)
        
    except Exception as e:
        await cl.Message(
            content=f"❌ An error occurred: {str(e)}",
            author="System"
        ).send()
