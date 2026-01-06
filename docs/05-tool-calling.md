# Phase 5: Tool Calling with Weather API

> ⏱️ **Time to complete**: 20 minutes

In this phase, we'll give our AI assistant the ability to call external tools! We'll integrate the WeatherAPI so the bot can fetch real-time weather data.

---

## 🎯 Learning Objectives

By the end of this phase, you will:
- Understand how LLM tool calling works
- Define tools using LangChain's tool decorator
- Build an agent that decides when to use tools
- See real-time weather data in your chat

---

## 🔧 What is Tool Calling?

Tool calling (also called "function calling") allows an LLM to:
1. Recognize when a user request requires external data/actions
2. Generate structured requests to call specific functions
3. Use the function results to formulate a response

### The Flow

```
User: "What's the weather in Tokyo?"
                    │
                    ▼
┌───────────────────────────────────────────────────────────┐
│  LLM analyzes the message and decides:                    │
│  "I need to call the get_weather tool with city='Tokyo'"  │
└───────────────────────────────────────────────────────────┘
                    │
                    ▼
┌───────────────────────────────────────────────────────────┐
│  Our code:                                                │
│  1. Receives the tool call request                        │
│  2. Executes get_weather("Tokyo")                         │
│  3. Calls WeatherAPI                                      │
│  4. Returns: "Tokyo: 8°C, Partly cloudy"                  │
└───────────────────────────────────────────────────────────┘
                    │
                    ▼
┌───────────────────────────────────────────────────────────┐
│  LLM receives the result and responds:                    │
│  "The current weather in Tokyo is 8°C and partly cloudy!" │
└───────────────────────────────────────────────────────────┘
```

---

## 🌤️ Step 1: Set Up WeatherAPI

First, let's add your WeatherAPI key to the `.env` file:

```bash
# Edit your .env file
GITHUB_TOKEN=ghp_your_token_here
WEATHER_API_KEY=your_weather_api_key_here
```

{% hint style="info" %}
**Don't have a key?** Get one free at [weatherapi.com](https://www.weatherapi.com/) - takes 2 minutes!
{% endhint %}

### Test the API (Optional)

You can test it directly:

```bash
curl "http://api.weatherapi.com/v1/current.json?key=YOUR_KEY&q=London"
```

---

## 🛠️ Step 2: Create the Weather Tool

Create a new file called `tools.py`:

```python
"""
Tool definitions for the AI assistant.
Tools are functions that the LLM can call to get external data.
"""

import os
import httpx
from langchain_core.tools import tool


@tool
def get_weather(city: str) -> str:
    """
    Get the current weather for a city.
    
    Args:
        city: The name of the city to get weather for (e.g., "London", "Tokyo", "New York")
    
    Returns:
        A string describing the current weather conditions.
    """
    api_key = os.getenv("WEATHER_API_KEY")
    
    if not api_key or api_key == "your_weather_api_key_here":
        return "Error: Weather API key not configured. Please add WEATHER_API_KEY to your .env file."
    
    try:
        # Call the WeatherAPI
        url = f"http://api.weatherapi.com/v1/current.json"
        params = {
            "key": api_key,
            "q": city,
            "aqi": "no"  # Don't need air quality data
        }
        
        response = httpx.get(url, params=params, timeout=10.0)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract relevant information
        location = data["location"]["name"]
        country = data["location"]["country"]
        temp_c = data["current"]["temp_c"]
        temp_f = data["current"]["temp_f"]
        condition = data["current"]["condition"]["text"]
        humidity = data["current"]["humidity"]
        wind_kph = data["current"]["wind_kph"]
        
        return f"""Weather for {location}, {country}:
🌡️ Temperature: {temp_c}°C ({temp_f}°F)
☁️ Condition: {condition}
💧 Humidity: {humidity}%
💨 Wind: {wind_kph} km/h"""
        
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            return f"Sorry, I couldn't find weather data for '{city}'. Please check the city name."
        return f"Error fetching weather: {e}"
    except httpx.RequestError as e:
        return f"Network error: Could not connect to weather service. {e}"
    except Exception as e:
        return f"Unexpected error: {e}"


# List of all available tools
TOOLS = [get_weather]
```

### 🔍 Understanding the @tool Decorator

The `@tool` decorator does several things:

1. **Converts function to a LangChain Tool** - Wraps it with metadata
2. **Extracts schema from docstring** - The description becomes tool documentation
3. **Parses type hints** - `city: str` tells the LLM what type of argument to provide
4. **Enables validation** - Ensures the LLM provides required parameters

The LLM receives this information as a "tool specification" and can decide when to call it.

---

## 🤖 Step 3: Create an Agent

Now we'll create an **agent** - an LLM that can decide when to use tools.

Create a new file called `app_agent.py`:

```python
"""
Chainlit app with tool-calling agent.
The agent can decide when to use tools like weather lookup.
"""

import os
from datetime import date
import chainlit as cl
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
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
    
    # Create the agent executor (runs the agent and handles tool calls)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=TOOLS,
        verbose=True,  # Set to True to see agent reasoning in console
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
    
    try:
        # Run the agent with streaming
        full_response = ""
        
        async for event in agent_executor.astream_events(agent_input, version="v2"):
            kind = event["event"]
            
            # Handle different event types
            if kind == "on_chat_model_stream":
                # Streaming tokens from the LLM
                content = event["data"]["chunk"].content
                if content:
                    full_response += content
                    await msg.stream_token(content)
                    
            elif kind == "on_tool_start":
                # Tool is about to be called
                tool_name = event["name"]
                tool_input = event["data"].get("input", {})
                await cl.Message(
                    content=f"🔧 Using tool: **{tool_name}**\nInput: `{tool_input}`",
                    author="System"
                ).send()
                
            elif kind == "on_tool_end":
                # Tool finished
                tool_output = event["data"].get("output", "")
                await cl.Message(
                    content=f"📊 Tool result:\n```\n{tool_output}\n```",
                    author="System"
                ).send()
        
        # Finalize the message
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
```

### 🔍 Understanding the Agent Components

| Component | Purpose |
|-----------|---------|
| `create_tool_calling_agent` | Creates an agent that can use tools |
| `AgentExecutor` | Runs the agent loop: think → act → observe → repeat |
| `agent_scratchpad` | Where the agent stores intermediate tool results |
| `astream_events` | Streams all events (tokens, tool calls, etc.) |

### The Agent Loop

```
┌──────────────────────────────────────────────────────────────────┐
│                         Agent Loop                                │
│                                                                   │
│   ┌─────────┐     ┌─────────────┐     ┌──────────┐              │
│   │  Think  │────▶│  Act (Tool) │────▶│  Observe │              │
│   └─────────┘     └─────────────┘     └──────────┘              │
│        ▲                                    │                    │
│        │                                    │                    │
│        └────────────────────────────────────┘                    │
│               (Repeat until done)                                │
│                                                                   │
│   When the agent decides it has enough info, it responds.        │
└──────────────────────────────────────────────────────────────────┘
```

---

## ▶️ Step 4: Test the Agent

Run the new agent app:

```bash
chainlit run app_agent.py -w
```

### Test Scenarios

**Test 1: Weather Query**
```
You: What's the weather in London?

System: 🔧 Using tool: get_weather
        Input: {'city': 'London'}

System: 📊 Tool result:
        Weather for London, United Kingdom:
        🌡️ Temperature: 7°C (44.6°F)
        ☁️ Condition: Overcast
        💧 Humidity: 87%
        💨 Wind: 15 km/h

Aria: The current weather in London is 7°C (44.6°F) with overcast 
      skies. It's quite humid at 87% with winds at 15 km/h. 
      You might want to bring a jacket!
```

**Test 2: Non-Weather Query**
```
You: What is Python?
Aria: Python is a high-level, interpreted programming language...
(No tool called - answers from knowledge)
```

**Test 3: Multiple Cities**
```
You: Compare the weather in Tokyo and Sydney
(Should call the tool twice!)
```

---

## 🎨 Step 5: Improve the UX (Optional)

Let's make the tool usage more visually appealing with Chainlit Steps:

Update the agent loop in `app_agent.py`:

```python
@cl.on_message
async def main(message: cl.Message):
    """Handle messages with the agent - improved UX version."""
    agent_executor = cl.user_session.get("agent_executor")
    chat_history = cl.user_session.get("chat_history")
    
    agent_input = {
        "input": message.content,
        "chat_history": chat_history,
        "current_date": date.today().strftime("%B %d, %Y"),
    }
    
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
                # Create a Step for the tool call
                tool_name = event["name"]
                tool_input = event["data"].get("input", {})
                current_step = cl.Step(name=f"🔧 {tool_name}", type="tool")
                current_step.input = str(tool_input)
                await current_step.send()
                
            elif kind == "on_tool_end":
                # Update the step with the result
                if current_step:
                    tool_output = event["data"].get("output", "")
                    current_step.output = tool_output
                    await current_step.update()
                    current_step = None
        
        if full_response:
            await msg.send()
        
        chat_history.append(HumanMessage(content=message.content))
        chat_history.append(AIMessage(content=full_response))
        cl.user_session.set("chat_history", chat_history)
        
    except Exception as e:
        await cl.Message(content=f"❌ Error: {str(e)}").send()
```

This creates collapsible "Steps" in the UI that show tool calls.

---

## 🗂️ Current Project Structure

```
langchain-chainlit-workshop/
├── .venv/
├── .env                    # Now has WEATHER_API_KEY
├── .gitignore
├── requirements.txt
├── test_github_models.py   
├── app.py                  # Phase 3
├── app_langchain.py        # Phase 4
├── app_agent.py            # Phase 5 - Agent with tools
└── tools.py                # Tool definitions
```

---

## ✅ Checkpoint: Tool Calling Works

| Test | Action | Expected |
|------|--------|----------|
| Weather works | Ask "Weather in Paris?" | Real weather data |
| Tool shown | Check UI | Tool call visible |
| Non-tool works | Ask "What is 2+2?" | Direct answer, no tool |
| Error handling | Ask "Weather in xyzabc" | Graceful error message |
| Memory works | Ask follow-up questions | Context remembered |

### 🎉 Tools Working?

**Amazing!** Your AI assistant can now take actions in the real world!

👉 **Next up: [Phase 6: MCP Integration](06-mcp-integration.md)**

---

## 🔍 Behind the Scenes: Tool Calling Flow

When the LLM decides to call a tool, here's what happens:

1. **LLM generates a tool call** (not regular text):
   ```json
   {
     "tool_calls": [{
       "name": "get_weather",
       "arguments": {"city": "Tokyo"}
     }]
   }
   ```

2. **AgentExecutor intercepts this** and runs the actual function

3. **Result is added to context** as a ToolMessage

4. **LLM sees the result** and generates a human-readable response

The LLM never directly calls APIs - it just indicates *what* it wants to do, and our code executes it.

---

## ❓ Common Issues

### "Weather API key not configured"
- Check your `.env` file has `WEATHER_API_KEY=your_key`
- Restart the Chainlit server after changing `.env`

### Agent never uses the tool
- Check the model supports tool calling (gpt-4o-mini does)
- Verify tools are passed to `create_tool_calling_agent`
- Check console output (`verbose=True`) for errors

### "Tool not found" errors
- Make sure `from tools import TOOLS` works
- Check `tools.py` is in the same directory

### Tool is called but response is empty
- Check the tool function returns a string
- Look at console output for errors
- Verify WeatherAPI is responding (test with curl)

### Rate limits
- WeatherAPI free tier has limits
- GitHub Models may rate limit tool-heavy usage
- Wait a minute and try again
