# Phase 6: MCP Integration

> ⏱️ **Time to complete**: 15 minutes

In this final phase, we'll integrate the **Model Context Protocol (MCP)** - an open standard that allows AI assistants to connect with external tools and data sources in a standardized way.

---

## 🎯 Learning Objectives

By the end of this phase, you will:
- Understand what MCP is and why it matters
- Create an MCP server that exposes tools
- Connect your agent to MCP tools
- See how MCP enables modular, reusable tool ecosystems

---

## 🌐 What is MCP?

**Model Context Protocol (MCP)** is an open protocol developed by Anthropic that standardizes how AI applications connect to external tools and data sources.

### The Problem MCP Solves

Before MCP, every AI application had to:
- Define its own tool format
- Build custom integrations for each tool
- Maintain separate code for each LLM provider

### The MCP Solution

```
┌─────────────────────────────────────────────────────────────────┐
│                    MCP Architecture                              │
│                                                                  │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐       │
│  │   Claude    │     │   ChatGPT   │     │ Your Agent  │       │
│  │   Desktop   │     │   (future)  │     │             │       │
│  └──────┬──────┘     └──────┬──────┘     └──────┬──────┘       │
│         │                   │                   │               │
│         └───────────────────┼───────────────────┘               │
│                             │                                    │
│                    ┌────────▼────────┐                          │
│                    │   MCP Protocol  │                          │
│                    │   (Standard)    │                          │
│                    └────────┬────────┘                          │
│                             │                                    │
│         ┌───────────────────┼───────────────────┐               │
│         │                   │                   │               │
│  ┌──────▼──────┐     ┌──────▼──────┐     ┌──────▼──────┐       │
│  │   Weather   │     │  Database   │     │   Custom    │       │
│  │   Server    │     │   Server    │     │   Server    │       │
│  └─────────────┘     └─────────────┘     └─────────────┘       │
│                                                                  │
│  One protocol, many servers, many clients!                      │
└─────────────────────────────────────────────────────────────────┘
```

### Benefits of MCP

| Benefit | Description |
|---------|-------------|
| **Standardization** | One protocol for all tools |
| **Reusability** | Write a tool once, use everywhere |
| **Modularity** | Add/remove tools without changing the agent |
| **Community** | Share tools with others |

---

## 🛠️ Step 1: Create an MCP Server

Let's create an MCP server that exposes our weather tool (and a new one!).

Create a new file called `mcp_server.py`:

```python
"""
MCP Server that exposes tools via the Model Context Protocol.

This server can be used by any MCP-compatible client (Claude Desktop, 
your Chainlit app, or other MCP clients).

Run with: python mcp_server.py
"""

import os
import asyncio
import httpx
from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Load environment variables
load_dotenv()

# Create the MCP server
server = Server("weather-tools")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """
    List all available tools.
    This is called by MCP clients to discover what tools are available.
    """
    return [
        Tool(
            name="get_weather",
            description="Get the current weather for a city. Provides temperature, conditions, humidity, and wind speed.",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city name (e.g., 'London', 'Tokyo', 'New York')"
                    }
                },
                "required": ["city"]
            }
        ),
        Tool(
            name="get_forecast",
            description="Get the weather forecast for the next 3 days for a city.",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city name"
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days (1-3)",
                        "default": 3
                    }
                },
                "required": ["city"]
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """
    Handle tool calls from MCP clients.
    """
    api_key = os.getenv("WEATHER_API_KEY")
    
    if not api_key or api_key == "your_weather_api_key_here":
        return [TextContent(
            type="text",
            text="Error: WEATHER_API_KEY not configured in .env file"
        )]
    
    if name == "get_weather":
        result = await fetch_current_weather(api_key, arguments.get("city", ""))
        return [TextContent(type="text", text=result)]
        
    elif name == "get_forecast":
        city = arguments.get("city", "")
        days = min(arguments.get("days", 3), 3)  # Max 3 days on free tier
        result = await fetch_forecast(api_key, city, days)
        return [TextContent(type="text", text=result)]
    
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def fetch_current_weather(api_key: str, city: str) -> str:
    """Fetch current weather from WeatherAPI."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://api.weatherapi.com/v1/current.json",
                params={"key": api_key, "q": city, "aqi": "no"},
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            
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
            return f"Could not find weather for '{city}'. Check the city name."
        return f"API error: {e}"
    except Exception as e:
        return f"Error: {e}"


async def fetch_forecast(api_key: str, city: str, days: int) -> str:
    """Fetch weather forecast from WeatherAPI."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://api.weatherapi.com/v1/forecast.json",
                params={"key": api_key, "q": city, "days": days, "aqi": "no"},
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            
            location = data["location"]["name"]
            country = data["location"]["country"]
            
            forecast_text = f"📅 {days}-Day Forecast for {location}, {country}:\n\n"
            
            for day in data["forecast"]["forecastday"]:
                date = day["date"]
                max_c = day["day"]["maxtemp_c"]
                min_c = day["day"]["mintemp_c"]
                condition = day["day"]["condition"]["text"]
                rain_chance = day["day"]["daily_chance_of_rain"]
                
                forecast_text += f"**{date}**\n"
                forecast_text += f"  🌡️ {min_c}°C - {max_c}°C\n"
                forecast_text += f"  ☁️ {condition}\n"
                forecast_text += f"  🌧️ Rain chance: {rain_chance}%\n\n"
            
            return forecast_text
            
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            return f"Could not find forecast for '{city}'."
        return f"API error: {e}"
    except Exception as e:
        return f"Error: {e}"


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
```

### 🔍 Understanding the MCP Server

| Component | Purpose |
|-----------|---------|
| `Server("name")` | Creates a named MCP server |
| `@server.list_tools()` | Decorator for tool discovery endpoint |
| `@server.call_tool()` | Decorator for tool execution endpoint |
| `Tool` | Definition of a tool with name, description, and JSON schema |
| `TextContent` | Return type for tool results |
| `stdio_server` | Communication via standard input/output |

---

## 🔌 Step 2: Create an MCP-Enabled Agent

Now let's modify our agent to use tools from the MCP server.

Create a new file called `app_mcp.py`:

```python
"""
Chainlit app that connects to MCP servers for tools.
Demonstrates the Model Context Protocol integration.
"""

import os
import asyncio
from datetime import date
from contextlib import asynccontextmanager
import chainlit as cl
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import StructuredTool
from langchain.agents import create_tool_calling_agent, AgentExecutor
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

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


# Agent prompt
AGENT_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are a helpful AI assistant named Aria with access to weather tools via MCP.

Available tools:
- get_weather: Get current weather for any city
- get_forecast: Get multi-day weather forecast

Always use these tools for weather-related queries. Be friendly and helpful!

Current date: {current_date}
"""
    ),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])


class MCPToolManager:
    """Manages connection to MCP servers and tool conversion."""
    
    def __init__(self):
        self.session: ClientSession | None = None
        self.tools: list[StructuredTool] = []
    
    async def connect(self, server_script: str):
        """Connect to an MCP server and load its tools."""
        server_params = StdioServerParameters(
            command="python",
            args=[server_script],
        )
        
        # Create the connection
        self._read, self._write = await asyncio.open_subprocess_pipe(server_params)
        self.session = ClientSession(self._read, self._write)
        await self.session.initialize()
        
        # Get available tools
        tools_response = await self.session.list_tools()
        
        # Convert MCP tools to LangChain tools
        for mcp_tool in tools_response.tools:
            langchain_tool = self._create_langchain_tool(mcp_tool)
            self.tools.append(langchain_tool)
        
        return self.tools
    
    def _create_langchain_tool(self, mcp_tool) -> StructuredTool:
        """Convert an MCP tool to a LangChain StructuredTool."""
        
        async def tool_func(**kwargs):
            """Call the MCP tool."""
            if self.session is None:
                return "Error: MCP session not connected"
            
            result = await self.session.call_tool(mcp_tool.name, kwargs)
            if result.content:
                return result.content[0].text
            return "No result"
        
        # Create the LangChain tool
        return StructuredTool.from_function(
            coroutine=tool_func,
            name=mcp_tool.name,
            description=mcp_tool.description,
        )
    
    async def close(self):
        """Close the MCP connection."""
        if self.session:
            await self.session.close()


# For simplicity in this workshop, we'll use a hybrid approach
# that works without running a separate MCP server process

async def get_mcp_inspired_tools():
    """
    Create tools that follow MCP patterns.
    In a real setup, these would come from an MCP server.
    """
    import httpx
    
    async def get_weather(city: str) -> str:
        """Get the current weather for a city."""
        api_key = os.getenv("WEATHER_API_KEY")
        if not api_key:
            return "Error: WEATHER_API_KEY not set"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "http://api.weatherapi.com/v1/current.json",
                    params={"key": api_key, "q": city},
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
                
                return f"""Weather for {data['location']['name']}, {data['location']['country']}:
🌡️ Temperature: {data['current']['temp_c']}°C ({data['current']['temp_f']}°F)
☁️ Condition: {data['current']['condition']['text']}
💧 Humidity: {data['current']['humidity']}%
💨 Wind: {data['current']['wind_kph']} km/h"""
        except Exception as e:
            return f"Error fetching weather: {e}"
    
    async def get_forecast(city: str, days: int = 3) -> str:
        """Get the weather forecast for a city."""
        api_key = os.getenv("WEATHER_API_KEY")
        if not api_key:
            return "Error: WEATHER_API_KEY not set"
        
        days = min(days, 3)  # Free tier limit
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "http://api.weatherapi.com/v1/forecast.json",
                    params={"key": api_key, "q": city, "days": days},
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
                
                forecast = f"📅 {days}-Day Forecast for {data['location']['name']}:\n\n"
                for day in data['forecast']['forecastday']:
                    forecast += f"**{day['date']}**: "
                    forecast += f"{day['day']['mintemp_c']}°C - {day['day']['maxtemp_c']}°C, "
                    forecast += f"{day['day']['condition']['text']}\n"
                
                return forecast
        except Exception as e:
            return f"Error fetching forecast: {e}"
    
    return [
        StructuredTool.from_function(
            coroutine=get_weather,
            name="get_weather",
            description="Get the current weather for a city. Input: city name."
        ),
        StructuredTool.from_function(
            coroutine=get_forecast,
            name="get_forecast", 
            description="Get weather forecast for 1-3 days. Input: city name and optional days (1-3)."
        ),
    ]


@cl.on_chat_start
async def start():
    """Initialize with MCP-style tools."""
    llm = get_llm()
    
    # Get tools (MCP-inspired pattern)
    tools = await get_mcp_inspired_tools()
    
    # Create agent
    agent = create_tool_calling_agent(llm, tools, AGENT_PROMPT)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
    )
    
    cl.user_session.set("agent_executor", agent_executor)
    cl.user_session.set("chat_history", [])
    
    await cl.Message(
        content="""👋 Hi! I'm Aria, powered by MCP-style tools!

I can help you with:
- 🌤️ **Current weather**: "What's the weather in London?"
- 📅 **Forecasts**: "Give me a 3-day forecast for Tokyo"

What would you like to know?"""
    ).send()


@cl.on_message
async def main(message: cl.Message):
    """Handle messages with MCP tools."""
    agent_executor = cl.user_session.get("agent_executor")
    chat_history = cl.user_session.get("chat_history")
    
    agent_input = {
        "input": message.content,
        "chat_history": chat_history,
        "current_date": date.today().strftime("%B %d, %Y"),
    }
    
    msg = cl.Message(content="")
    full_response = ""
    
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
                step = cl.Step(name=f"🔧 MCP Tool: {tool_name}", type="tool")
                step.input = str(tool_input)
                await step.send()
                cl.user_session.set("current_step", step)
                
            elif kind == "on_tool_end":
                step = cl.user_session.get("current_step")
                if step:
                    step.output = event["data"].get("output", "")
                    await step.update()
        
        if full_response:
            await msg.send()
        
        chat_history.append(HumanMessage(content=message.content))
        chat_history.append(AIMessage(content=full_response))
        cl.user_session.set("chat_history", chat_history)
        
    except Exception as e:
        await cl.Message(content=f"❌ Error: {str(e)}").send()
```

---

## ▶️ Step 3: Run and Test

Start the MCP-enabled app:

```bash
chainlit run app_mcp.py -w
```

### Test the New Features

**Test 1: Current Weather**
```
You: What's the weather in Berlin?
```

**Test 2: Forecast (New!)**
```
You: Give me a 3-day forecast for San Francisco
```

**Test 3: Combined Query**
```
You: I'm planning a trip to Rome. What's the weather like now and for the next few days?
```

---

## 🏗️ Understanding MCP Architecture

### How MCP Works in Production

In a full MCP setup:

```
┌─────────────────────────────────────────────────────────┐
│                    Your Application                      │
│                                                          │
│    ┌───────────────┐        ┌─────────────────┐        │
│    │  MCP Client   │◄──────▶│  MCP Server(s)  │        │
│    │  (in agent)   │ stdio  │  (separate      │        │
│    │               │  or    │   processes)    │        │
│    │               │ HTTP   │                 │        │
│    └───────────────┘        └─────────────────┘        │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Benefits**:
- Servers can be written in any language
- Servers can be shared between applications
- Tools can be added/removed without restarting the agent
- Security: servers run in separate processes

### MCP Message Types

| Message | Direction | Purpose |
|---------|-----------|---------|
| `list_tools` | Client → Server | Discover available tools |
| `call_tool` | Client → Server | Execute a tool |
| `tools` | Server → Client | Tool definitions |
| `result` | Server → Client | Tool execution result |

---

## 🌍 Real-World MCP Ecosystem

MCP is being adopted across the AI ecosystem:

### Available MCP Servers
- **Filesystem** - Read/write local files
- **GitHub** - Interact with repositories
- **Postgres/SQLite** - Database queries
- **Slack** - Send messages
- **Google Drive** - File access
- **And many more!**

### Where MCP is Used
- **Claude Desktop** - Native MCP support
- **Zed Editor** - MCP tool integration  
- **Custom agents** - Like what we built!

---

## 🗂️ Final Project Structure

```
langchain-chainlit-workshop/
├── .venv/
├── .env                    
├── .gitignore
├── requirements.txt
├── test_github_models.py   
├── app.py                  # Phase 3: Basic Chainlit
├── app_langchain.py        # Phase 4: LangChain chains
├── app_agent.py            # Phase 5: Tool-calling agent
├── app_mcp.py              # Phase 6: MCP integration
├── tools.py                # Tool definitions
└── mcp_server.py           # MCP server (for reference)
```

---

## ✅ Final Checkpoint: Complete Agent

| Feature | Test | Expected |
|---------|------|----------|
| Current weather | Ask for any city | Real-time data |
| Forecast | Request 3-day forecast | Multi-day data |
| Tool visibility | Check UI | Steps show tool calls |
| Memory | Multi-turn conversation | Context preserved |
| Error handling | Invalid city name | Graceful message |

---

## 🎉 Congratulations!

You've completed the workshop! You've built:

1. ✅ A chat interface with **Chainlit**
2. ✅ LLM integration with **GitHub Models** (free!)
3. ✅ Conversation memory with **LangChain**
4. ✅ Tool calling with **WeatherAPI**
5. ✅ MCP-style architecture for extensibility

### What's Next?

- **Add more tools**: File search, web browsing, calculations
- **Deploy**: Host on Hugging Face Spaces, Railway, or your own server
- **Try real MCP servers**: Connect to community-built servers
- **Build your own MCP server**: Expose your own APIs

---

## 📚 Resources

- [LangChain Documentation](https://python.langchain.com/)
- [Chainlit Documentation](https://docs.chainlit.io/)
- [MCP Specification](https://modelcontextprotocol.io/)
- [GitHub Models](https://github.com/marketplace/models)
- [WeatherAPI Docs](https://www.weatherapi.com/docs/)

---

## ❓ Common Issues

### MCP server won't start
- Check Python is in your PATH
- Ensure all dependencies are installed
- Look for syntax errors in `mcp_server.py`

### Tool calls timeout
- WeatherAPI may be slow
- Check your internet connection
- Increase timeout values

### "Module mcp not found"
- Run: `pip install mcp`
- Make sure virtual environment is activated

### Agent ignores tools
- Verify the model supports tool calling
- Check tool descriptions are clear
- Ensure tools are passed to the agent correctly
