# Phase 4: LangChain Integration

> ⏱️ **Time to complete**: 15 minutes

In this phase, we'll restructure our application using LangChain's powerful abstractions. This prepares us for adding tools and building a proper agent in the next phases.

---

## 🎯 Learning Objectives

By the end of this phase, you will:
- Understand LangChain's core concepts (chains, prompts, output parsers)
- Refactor the app to use prompt templates
- Add structured output handling
- Prepare the foundation for tool integration

---

## 🔗 What is LangChain?

LangChain is a framework for building applications with language models. It provides:

- **Standardized interfaces** - Work with any LLM the same way
- **Composability** - Chain operations together
- **Tool integration** - Let LLMs call functions
- **Memory management** - Track conversation history
- **Agents** - LLMs that can decide what actions to take

### Core Concepts

```
┌─────────────────────────────────────────────────────────────┐
│                    LangChain Architecture                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌─────────────┐    ┌──────────────┐   │
│  │    Prompt    │───▶│     LLM     │───▶│    Output    │   │
│  │   Template   │    │   (Model)   │    │    Parser    │   │
│  └──────────────┘    └─────────────┘    └──────────────┘   │
│         │                   │                   │           │
│         └───────────────────┴───────────────────┘           │
│                           │                                  │
│                    ┌──────▼──────┐                          │
│                    │    Chain    │                          │
│                    └─────────────┘                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

| Concept | Purpose |
|---------|---------|
| **Prompt Template** | Reusable message templates with variables |
| **LLM** | The language model (GPT-4o, etc.) |
| **Output Parser** | Structures the LLM's raw text output |
| **Chain** | Connects components together |

---

## 📝 Step 1: Create a Prompt Template

Instead of hardcoding the system prompt, let's use a ChatPromptTemplate.

Create a new file called `app_langchain.py`:

```python
"""
Chainlit app with proper LangChain integration.
Uses prompt templates for structured prompting.
"""

import os
import chainlit as cl
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

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


# Define a structured prompt template
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
    # This placeholder will be filled with conversation history
    MessagesPlaceholder(variable_name="chat_history"),
    # The current user message
    ("human", "{input}"),
])


@cl.on_chat_start
async def start():
    """Initialize the chat session."""
    from datetime import date
    
    # Store components in session
    cl.user_session.set("llm", get_llm())
    cl.user_session.set("prompt", PROMPT_TEMPLATE)
    cl.user_session.set("chat_history", [])
    cl.user_session.set("current_date", date.today().strftime("%B %d, %Y"))
    
    await cl.Message(
        content="👋 Hi! I'm Aria, your AI assistant. How can I help you today?"
    ).send()


@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages using LangChain chain."""
    # Retrieve session data
    llm = cl.user_session.get("llm")
    prompt = cl.user_session.get("prompt")
    chat_history = cl.user_session.get("chat_history")
    current_date = cl.user_session.get("current_date")
    
    # Format the prompt with variables
    formatted_messages = prompt.format_messages(
        current_date=current_date,
        chat_history=chat_history,
        input=message.content,
    )
    
    # Stream the response
    msg = cl.Message(content="")
    full_response = ""
    
    async for chunk in llm.astream(formatted_messages):
        if chunk.content:
            full_response += chunk.content
            await msg.stream_token(chunk.content)
    
    await msg.send()
    
    # Update chat history
    chat_history.append(HumanMessage(content=message.content))
    chat_history.append(AIMessage(content=full_response))
    cl.user_session.set("chat_history", chat_history)
```

### 🔍 What's New?

| Component | Purpose |
|-----------|---------|
| `ChatPromptTemplate` | Defines the structure of messages sent to the LLM |
| `MessagesPlaceholder` | Dynamically inserts conversation history |
| `format_messages()` | Fills in the template variables |
| `{current_date}` | Template variable - notice how the bot now knows today's date |

---

## ▶️ Step 2: Test the New App

Stop the previous server (Ctrl+C) and run the new one:

```bash
chainlit run app_langchain.py -w
```

Test it:
1. Ask "What's today's date?" - It should know!
2. Have a conversation and verify memory works
3. Notice the assistant identifies as "Aria"

---

## ⛓️ Step 3: Create a Proper Chain

LangChain's power comes from chaining components. Let's use LCEL (LangChain Expression Language).

Update `app_langchain.py`:

```python
"""
Chainlit app with LangChain LCEL chains.
Demonstrates modern LangChain patterns.
"""

import os
from datetime import date
import chainlit as cl
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

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
    
    The chain: input -> add metadata -> prompt -> llm -> output
    """
    
    def add_current_date(inputs: dict) -> dict:
        """Add the current date to the inputs."""
        inputs["current_date"] = date.today().strftime("%B %d, %Y")
        return inputs
    
    # LCEL chain using the pipe operator
    chain = (
        RunnableLambda(add_current_date)  # Add metadata
        | PROMPT_TEMPLATE                   # Format the prompt
        | llm                               # Send to LLM
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
```

### 🔍 Understanding LCEL

LCEL (LangChain Expression Language) uses the pipe operator `|` to chain components:

```python
chain = component_a | component_b | component_c
```

This is equivalent to:
```python
result = component_c(component_b(component_a(input)))
```

**Benefits**:
- Readable left-to-right flow
- Each component transforms the data
- Built-in streaming support
- Easy to add/remove steps

### The Chain Flow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────┐
│   Input     │───▶│  Add Date   │───▶│   Prompt    │───▶│   LLM   │
│   Dict      │    │  Lambda     │    │  Template   │    │         │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────┘
      │                   │                  │                │
  {input,             {input,           [messages]      AI Response
   chat_history}       chat_history,
                       current_date}
```

---

## 🏗️ Step 4: Prepare for Tools (Agent Preview)

Let's add a preview of what's coming - we'll modify the prompt to make the assistant aware it will have tools.

Update the system message in `PROMPT_TEMPLATE`:

```python
PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are a helpful AI assistant named Aria. You have the following traits:
- Friendly and conversational tone
- Concise but thorough answers
- You admit when you don't know something
- You can help with coding, writing, analysis, and general questions

In future versions, you will have access to tools like:
- Weather lookup: Get current weather for any city
- More tools coming soon!

When a user asks about weather, acknowledge that this feature is coming soon.

Current date: {current_date}
"""
    ),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
])
```

Test it:
- Ask "What's the weather in Paris?"
- The bot should mention the feature is coming soon

---

## 🗂️ Current Project Structure

```
langchain-chainlit-workshop/
├── .venv/
├── .env                    
├── .gitignore
├── requirements.txt
├── test_github_models.py   
├── app.py                  # Basic version (Phase 3)
└── app_langchain.py        # LangChain version (Phase 4)
```

---

## ✅ Checkpoint: LangChain Integration Complete

| Test | How | Expected |
|------|-----|----------|
| App runs | `chainlit run app_langchain.py -w` | No errors |
| Date works | Ask "What's today's date?" | Correct date |
| Memory works | Multi-turn conversation | Context remembered |
| Name works | Ask "What's your name?" | "Aria" |
| Weather preview | Ask about weather | "Coming soon" message |

### 🎉 Chain Working?

**Excellent!** You now understand LangChain's core patterns.

👉 **Next up: [Phase 5: Tool Calling with Weather API](05-tool-calling.md)**

---

## 🔍 Behind the Scenes: How Chains Work

When you call `chain.astream(input)`:

1. **Input flows through each component**:
   ```
   {"input": "Hello", "chat_history": []}
   ```

2. **RunnableLambda adds date**:
   ```
   {"input": "Hello", "chat_history": [], "current_date": "January 6, 2026"}
   ```

3. **Prompt template formats messages**:
   ```python
   [
       SystemMessage(content="You are Aria...Current date: January 6, 2026"),
       HumanMessage(content="Hello")
   ]
   ```

4. **LLM processes and streams**:
   ```
   AIMessageChunk(content="Hi")
   AIMessageChunk(content=" there")
   AIMessageChunk(content="!")
   ```

5. **We capture chunks and display them**

---

## ❓ Common Issues

### "RunnableLambda is not defined"
Add the import:
```python
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
```

### Chain doesn't stream properly
- Make sure `streaming=True` in `ChatOpenAI`
- Use `chain.astream()` not `chain.invoke()`
- Check the async for loop captures chunks correctly

### "TypeError: 'coroutine' object is not iterable"
- Make sure you're using `async for` not regular `for`
- Ensure the function is defined with `async def`

### Date is wrong
- Check your system clock
- The `date.today()` uses your local timezone
