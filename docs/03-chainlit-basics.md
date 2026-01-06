# Phase 3: Your First Chainlit Chat App

> ⏱️ **Time to complete**: 15 minutes

In this phase, we'll build a real-time chat interface using Chainlit. You'll see messages appear with streaming, just like ChatGPT!

---

## 🎯 Learning Objectives

By the end of this phase, you will:
- Understand Chainlit's event-driven architecture
- Create a basic chat application
- See streaming responses in action
- Learn about message handling and decorators

---

## 💬 What is Chainlit?

Chainlit is an open-source Python framework for building conversational AI interfaces. It provides:

- **Real-time chat UI** - Beautiful, responsive interface out of the box
- **Streaming support** - Show responses as they're generated
- **Message history** - Automatic conversation tracking
- **Easy deployment** - Run locally or deploy anywhere
- **LLM integrations** - Works with LangChain, OpenAI, and more

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Browser (UI)                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │           Chainlit Chat Interface               │    │
│  │  ┌─────────────────────────────────────────┐   │    │
│  │  │  User types message                      │   │    │
│  │  │  ↓                                       │   │    │
│  │  │  @cl.on_message handler                  │   │    │
│  │  │  ↓                                       │   │    │
│  │  │  Process with LLM                        │   │    │
│  │  │  ↓                                       │   │    │
│  │  │  Stream response back                    │   │    │
│  │  └─────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                         │
                         │ WebSocket
                         ↓
┌─────────────────────────────────────────────────────────┐
│                  Python Backend                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │  app.py                                          │    │
│  │  - @cl.on_chat_start (session init)             │    │
│  │  - @cl.on_message (handle user input)           │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

---

## 📝 Step 1: Create a Basic Echo App

Let's start with the simplest possible Chainlit app - an echo bot.

Create a file called `app.py`:

```python
"""
Basic Chainlit app - Echo Bot
This demonstrates the fundamental Chainlit patterns.
"""

import chainlit as cl


@cl.on_chat_start
async def start():
    """
    Called when a new chat session starts.
    This is where you initialize per-session state.
    """
    # Send a welcome message
    await cl.Message(
        content="👋 Hello! I'm an echo bot. Send me a message and I'll repeat it back!"
    ).send()


@cl.on_message
async def main(message: cl.Message):
    """
    Called every time the user sends a message.
    
    Args:
        message: The user's message object containing:
            - content: The text of the message
            - author: Who sent it
            - elements: Any attached files/images
    """
    # Get what the user typed
    user_input = message.content
    
    # Echo it back
    await cl.Message(
        content=f"🔄 You said: {user_input}"
    ).send()
```

### 🔍 Understanding the Code

| Component | Purpose |
|-----------|---------|
| `@cl.on_chat_start` | Decorator that marks a function to run when a new session begins |
| `@cl.on_message` | Decorator that marks a function to run for each user message |
| `async def` | Chainlit uses async/await for non-blocking operations |
| `cl.Message(content=...).send()` | Creates and sends a message to the UI |

---

## ▶️ Step 2: Run the App

Start the Chainlit development server:

```bash
chainlit run app.py -w
```

The `-w` flag enables **watch mode** - the app auto-reloads when you save changes.

**Expected output**:
```
2026-01-06 10:00:00 - Chainlit - INFO - Your app is available at http://localhost:8000
```

### Open the Chat Interface

1. Open your browser to **http://localhost:8000**
2. You should see the chat interface
3. The welcome message should appear automatically
4. Type something and press Enter
5. See your message echoed back!

{% hint style="info" %}
**Leave the server running** - we'll modify the code and it will auto-reload.
{% endhint %}

---

## 🤖 Step 3: Add the LLM

Now let's replace the echo with actual AI responses.

Update `app.py`:

```python
"""
Chainlit app with GitHub Models integration.
"""

import os
import chainlit as cl
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()


def get_llm():
    """Create and return the LLM client."""
    return ChatOpenAI(
        model="gpt-4o-mini",
        api_key=os.getenv("GITHUB_TOKEN"),
        base_url="https://models.inference.ai.azure.com",
        temperature=0.7,
        streaming=True,  # Enable streaming!
    )


@cl.on_chat_start
async def start():
    """Initialize the chat session."""
    # Store the LLM in the user session
    cl.user_session.set("llm", get_llm())
    
    await cl.Message(
        content="👋 Hello! I'm an AI assistant powered by GitHub Models. How can I help you today?"
    ).send()


@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages."""
    # Get the LLM from session
    llm = cl.user_session.get("llm")
    
    # Create a message placeholder for streaming
    msg = cl.Message(content="")
    
    # Stream the response
    async for chunk in llm.astream(message.content):
        # Each chunk contains a piece of the response
        if chunk.content:
            await msg.stream_token(chunk.content)
    
    # Send the final message (marks streaming as complete)
    await msg.send()
```

### 🔍 What's New Here?

| Code | Explanation |
|------|-------------|
| `streaming=True` | Tells the LLM to return responses in chunks |
| `cl.user_session` | Per-session storage - each user gets their own LLM instance |
| `llm.astream()` | Async generator that yields response chunks |
| `msg.stream_token()` | Appends text to the message in real-time |

### Test It

1. Save the file (Chainlit should auto-reload)
2. Refresh your browser
3. Ask a question like "What is Python?"
4. Watch the response stream in character by character! ✨

---

## 💾 Step 4: Add Conversation Memory

Right now, the bot forgets everything after each message. Let's add memory.

Update `app.py`:

```python
"""
Chainlit app with conversation memory.
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
    
    # Update the session (not strictly necessary as it's a mutable list)
    cl.user_session.set("messages", messages)
```

### 🔍 Understanding Message Types

LangChain uses different message types:

| Type | Purpose | Example |
|------|---------|---------|
| `SystemMessage` | Instructions for the AI | "You are a helpful assistant" |
| `HumanMessage` | What the user says | "What is Python?" |
| `AIMessage` | What the assistant replied | "Python is a programming language..." |

The full conversation history is sent with each request, allowing the model to remember context.

### Test Memory

1. Save and refresh
2. Say: "My name is Alex"
3. Then ask: "What's my name?"
4. The bot should remember! 🎉

---

## 🗂️ Current Project Structure

```
langchain-chainlit-workshop/
├── .venv/
├── .env                    
├── .gitignore
├── requirements.txt
├── test_github_models.py   
└── app.py                  # Your Chainlit app
```

---

## ✅ Checkpoint: Chainlit Chat Working

Test your application:

| Test | How | Expected |
|------|-----|----------|
| App starts | `chainlit run app.py -w` | No errors, shows URL |
| UI loads | Open http://localhost:8000 | Chat interface appears |
| Welcome message | Start new chat | See greeting |
| AI responds | Ask "What is 2+2?" | Get streamed response |
| Memory works | Say your name, then ask for it | Bot remembers |

### 🎉 All Working?

**Fantastic!** You've built a fully functional chat application!

👉 **Next up: [Phase 4: LangChain Integration](04-langchain.md)**

---

## ❓ Common Issues

### "Module 'chainlit' has no attribute 'on_message'"
- Make sure you're using Chainlit 2.x
- Run: `pip show chainlit` to check version

### Page shows "Cannot connect to server"
- Make sure `chainlit run app.py -w` is running
- Check for error messages in the terminal
- Try restarting the server

### Streaming doesn't work (responses appear all at once)
- Verify `streaming=True` is set in `ChatOpenAI()`
- Make sure you're using `astream()` not `invoke()`
- Check that you're calling `stream_token()` in the loop

### "Session not found" errors
- Refresh the browser page
- Each browser tab is a separate session
- Session data is lost when the server restarts

### Messages are slow
- GitHub Models may have latency
- First request is often slower (cold start)
- Check your internet connection
