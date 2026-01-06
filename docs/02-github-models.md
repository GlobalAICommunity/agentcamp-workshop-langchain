# Phase 2: GitHub Models Configuration

> ⏱️ **Time to complete**: 10 minutes

In this phase, we'll set up access to GitHub Models - a **completely free** way to use powerful LLMs like GPT-4o, Llama, and more. No credit card required!

---

## 🎯 Learning Objectives

By the end of this phase, you will:
- Understand what GitHub Models offers
- Generate a Personal Access Token (PAT)
- Configure your environment for API access
- Test the connection to verify it works

---

## 🤖 What is GitHub Models?

GitHub Models is a free service that provides:
- Access to top LLMs (GPT-4o, GPT-4o-mini, Llama 3.3, Mistral, and more)
- OpenAI-compatible API endpoints
- No credit card or payment required
- Rate limits suitable for development and learning

### Available Models (as of 2026)

| Model | Provider | Best For |
|-------|----------|----------|
| `gpt-4o` | OpenAI | Complex reasoning, best quality |
| `gpt-4o-mini` | OpenAI | Fast responses, good quality |
| `Meta-Llama-3.3-70B-Instruct` | Meta | Open-source alternative |
| `Mistral-Large-2411` | Mistral | European AI option |

We'll use **`gpt-4o-mini`** in this workshop for fast responses.

---

## 🔑 Step 1: Generate a GitHub Personal Access Token

A Personal Access Token (PAT) is like a password that allows applications to authenticate with GitHub on your behalf.

### Navigate to Token Settings

1. Go to [github.com](https://github.com) and log in
2. Click your **profile picture** (top right)
3. Click **Settings**
4. Scroll down in the left sidebar to **Developer settings** (at the bottom)
5. Click **Personal access tokens** → **Tokens (classic)**

Or go directly to: [github.com/settings/tokens](https://github.com/settings/tokens)

### Create a New Token

1. Click **"Generate new token"** → **"Generate new token (classic)"**

2. Fill in the form:
   - **Note**: `Workshop - LangChain Chainlit` (or any description)
   - **Expiration**: `7 days` (enough for the workshop)
   - **Scopes**: No scopes needed! Leave all boxes **unchecked**

{% hint style="warning" %}
**Important**: For GitHub Models, you don't need any scopes selected. A token with no scopes can still access the Models API.
{% endhint %}

3. Scroll down and click **"Generate token"**

4. **COPY THE TOKEN IMMEDIATELY!** 
   
   You'll see something like: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   
   ⚠️ This is shown only once. If you lose it, you'll need to generate a new one.

---

## ⚙️ Step 2: Configure Your Environment

Now let's add the token to your `.env` file:

```bash
# Open the .env file in your editor and replace the placeholder
# It should look like this:

GITHUB_TOKEN=ghp_your_actual_token_here
WEATHER_API_KEY=your_weather_api_key_here
```

### Using the Terminal

```bash
# On macOS/Linux - replace with your actual token
sed -i '' 's/your_github_token_here/ghp_your_actual_token/' .env

# Or just edit with any text editor:
# VS Code: code .env
# Nano: nano .env
# Vim: vim .env
```

---

## 🔍 Step 3: Understand the Architecture

Here's what happens when we call GitHub Models:

```
┌─────────────────┐     ┌──────────────────────┐     ┌─────────────┐
│   Your App      │────▶│   GitHub Models API  │────▶│  LLM Model  │
│   (LangChain)   │     │   (OpenAI Compatible)│     │  (GPT-4o)   │
└─────────────────┘     └──────────────────────┘     └─────────────┘
         │                        │
         │                        │
    Uses GITHUB_TOKEN        Routes to model
    for authentication       you specified
```

### Key Details

| Setting | Value |
|---------|-------|
| **API Base URL** | `https://models.inference.ai.azure.com` |
| **API Format** | OpenAI-compatible |
| **Authentication** | Bearer token (your GitHub PAT) |
| **Model Name** | e.g., `gpt-4o-mini` |

Because the API is OpenAI-compatible, we can use `langchain-openai` package with a custom base URL.

---

## 🧪 Step 4: Test the Connection

Let's verify everything works with a simple test script.

Create a file called `test_github_models.py`:

```python
"""
Test script to verify GitHub Models connection.
Run with: python test_github_models.py
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load environment variables from .env file
load_dotenv()

def main():
    # Get the token from environment
    github_token = os.getenv("GITHUB_TOKEN")
    
    if not github_token or github_token == "your_github_token_here":
        print("❌ Error: GITHUB_TOKEN not set in .env file")
        print("   Please add your GitHub token to the .env file")
        return
    
    print("🔄 Testing connection to GitHub Models...")
    
    # Create the LLM client
    # We use ChatOpenAI but point it to GitHub's endpoint
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=github_token,
        base_url="https://models.inference.ai.azure.com",
        temperature=0.7,
    )
    
    try:
        # Send a simple test message
        response = llm.invoke("Say 'Hello, Workshop!' and nothing else.")
        print(f"✅ Success! Model responded: {response.content}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("- Make sure your GitHub token is valid")
        print("- Check your internet connection")
        print("- Verify the token hasn't expired")

if __name__ == "__main__":
    main()
```

Run the test:

```bash
python test_github_models.py
```

**Expected output**:
```
🔄 Testing connection to GitHub Models...
✅ Success! Model responded: Hello, Workshop!
```

---

## 🔍 Behind the Scenes: What Just Happened?

When you ran the test script:

1. **`load_dotenv()`** - Read the `.env` file and loaded `GITHUB_TOKEN` into the environment

2. **`ChatOpenAI(...)`** - Created an LLM client with:
   - Custom `base_url` pointing to GitHub's API
   - Your GitHub token as the `api_key`
   - Model set to `gpt-4o-mini`

3. **`llm.invoke(...)`** - Sent an HTTP POST request to:
   ```
   https://models.inference.ai.azure.com/chat/completions
   ```
   With headers:
   ```
   Authorization: Bearer ghp_xxxxx
   Content-Type: application/json
   ```
   And body:
   ```json
   {
     "model": "gpt-4o-mini",
     "messages": [{"role": "user", "content": "Say 'Hello, Workshop!'..."}],
     "temperature": 0.7
   }
   ```

4. **Response** - GitHub routed the request to the GPT-4o-mini model and returned the completion

---

## 🗂️ Current Project Structure

```
langchain-chainlit-workshop/
├── .venv/
├── .env                    # Now contains your GITHUB_TOKEN
├── .gitignore
├── requirements.txt
└── test_github_models.py   # Test script (can delete after testing)
```

---

## ✅ Checkpoint: GitHub Models Connected

| Check | Result |
|-------|--------|
| Token generated | ✓ Have a `ghp_xxx` token |
| Token saved | ✓ In `.env` file |
| Connection works | ✓ `test_github_models.py` shows success |

### 🎉 Connection Working?

**Excellent!** You now have free access to powerful LLMs.

👉 **Next up: [Phase 3: Your First Chainlit Chat App](03-chainlit-basics.md)**

---

## ❓ Common Issues

### "401 Unauthorized" or "Authentication failed"
- Double-check your token is copied correctly (starts with `ghp_`)
- Make sure there are no extra spaces in the `.env` file
- Verify the token hasn't expired

### "Model not found" or "404"
- Check the model name is exactly `gpt-4o-mini` (case-sensitive)
- Try `gpt-4o` if mini doesn't work

### "Rate limit exceeded"
- GitHub Models has rate limits for free tier
- Wait a minute and try again
- For workshops, the facilitator may have backup tokens

### Token appears in git history
- If you accidentally committed your token:
  1. Revoke it immediately on GitHub
  2. Generate a new one
  3. Update your `.env` file
  4. Add `.env` to `.gitignore` (already done if you followed Phase 1)
