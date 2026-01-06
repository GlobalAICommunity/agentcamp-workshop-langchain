"""
Phase 6 Solution: MCP-Style Integration with Weather Tools
Run with: chainlit run app.py -w
"""

import os
from datetime import date
import chainlit as cl
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import StructuredTool
from langchain.agents import create_tool_calling_agent, AgentExecutor
import httpx

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


async def get_mcp_inspired_tools():
    """
    Create tools that follow MCP patterns.
    In a real setup, these would come from an MCP server.
    """
    
    async def get_weather(city: str) -> str:
        """Get the current weather for a city."""
        api_key = os.getenv("WEATHER_API_KEY")
        if not api_key or api_key == "your_weather_api_key_here":
            return "Error: WEATHER_API_KEY not set in .env file"
        
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
                return f"Could not find weather for '{city}'. Please check the city name."
            return f"API error: {e}"
        except Exception as e:
            return f"Error fetching weather: {e}"
    
    async def get_forecast(city: str, days: int = 3) -> str:
        """Get the weather forecast for a city."""
        api_key = os.getenv("WEATHER_API_KEY")
        if not api_key or api_key == "your_weather_api_key_here":
            return "Error: WEATHER_API_KEY not set in .env file"
        
        days = min(max(days, 1), 3)  # Clamp to 1-3 (free tier limit)
        
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
                
                forecast = f"📅 {days}-Day Forecast for {location}, {country}:\n\n"
                
                for day in data["forecast"]["forecastday"]:
                    date_str = day["date"]
                    max_c = day["day"]["maxtemp_c"]
                    min_c = day["day"]["mintemp_c"]
                    condition = day["day"]["condition"]["text"]
                    rain_chance = day["day"]["daily_chance_of_rain"]
                    
                    forecast += f"**{date_str}**\n"
                    forecast += f"  🌡️ {min_c}°C - {max_c}°C\n"
                    forecast += f"  ☁️ {condition}\n"
                    forecast += f"  🌧️ Rain chance: {rain_chance}%\n\n"
                
                return forecast
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                return f"Could not find forecast for '{city}'."
            return f"API error: {e}"
        except Exception as e:
            return f"Error fetching forecast: {e}"
    
    return [
        StructuredTool.from_function(
            coroutine=get_weather,
            name="get_weather",
            description="Get the current weather for a city. Input: city name (e.g., 'London', 'Tokyo')."
        ),
        StructuredTool.from_function(
            coroutine=get_forecast,
            name="get_forecast", 
            description="Get weather forecast for 1-3 days. Input: city name and optional days (1-3, default 3)."
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
