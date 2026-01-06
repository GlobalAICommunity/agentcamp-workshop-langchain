# Phase 1: Environment Setup

> ⏱️ **Time to complete**: 10 minutes

In this phase, we'll create our project folder, set up a Python virtual environment, and install the core dependencies. This foundation ensures everyone has a consistent, isolated development environment.

---

## 🎯 Learning Objectives

By the end of this phase, you will:
- Understand why virtual environments matter
- Create an isolated Python environment for the project
- Install the core packages we'll use throughout the workshop

---

## 📁 Step 1: Create the Project Folder

Open your terminal and run:

```bash
# Create and navigate to the project folder
mkdir langchain-chainlit-workshop
cd langchain-chainlit-workshop
```

---

## 🐍 Step 2: Create a Virtual Environment

A **virtual environment** is an isolated Python installation. This means:
- Packages we install won't affect your system Python
- We can have specific versions without conflicts
- Easy to delete and recreate if something goes wrong

{% tabs %}
{% tab title="Using uv (Recommended)" %}
```bash
# Create virtual environment
uv venv

# Activate it
# macOS/Linux:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate
```
{% endtab %}

{% tab title="Using pip/venv" %}
```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
# macOS/Linux:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate
```
{% endtab %}
{% endtabs %}

### 🔍 What Just Happened?

When you created the virtual environment:
1. Python created a `.venv` folder in your project
2. This folder contains a copy of the Python interpreter
3. It has its own `site-packages` directory for libraries
4. When activated, your shell's `PATH` is modified to use this Python first

**You'll know it's active when you see `(.venv)` at the start of your terminal prompt.**

---

## 📦 Step 3: Create Requirements File

Create a file called `requirements.txt` with our core dependencies:

```bash
# Create the requirements file
cat > requirements.txt << 'EOF'
# Chat UI Framework
chainlit>=2.0.0

# LLM Orchestration
langchain>=0.3.0
langchain-openai>=0.3.0

# HTTP requests for tools
httpx>=0.27.0

# Environment variable management
python-dotenv>=1.0.0

# MCP Integration
mcp>=1.0.0
EOF
```

Or manually create `requirements.txt` with this content:

```txt
# Chat UI Framework
chainlit>=2.0.0

# LLM Orchestration
langchain>=0.3.0
langchain-openai>=0.3.0

# HTTP requests for tools
httpx>=0.27.0

# Environment variable management
python-dotenv>=1.0.0

# MCP Integration
mcp>=1.0.0
```

### 🔍 What Are These Packages?

| Package | Purpose |
|---------|---------|
| `chainlit` | Provides the chat web interface - handles UI, message history, and real-time streaming |
| `langchain` | Framework for building LLM applications - chains, agents, tools |
| `langchain-openai` | OpenAI-compatible integration (works with GitHub Models) |
| `httpx` | Modern async HTTP client for calling external APIs |
| `python-dotenv` | Loads environment variables from `.env` files |
| `mcp` | Model Context Protocol for standardized agent communication |

---

## 📥 Step 4: Install Dependencies

{% tabs %}
{% tab title="Using uv (Recommended)" %}
```bash
uv pip install -r requirements.txt
```
This typically completes in 5-10 seconds! ⚡
{% endtab %}

{% tab title="Using pip" %}
```bash
pip install -r requirements.txt
```
This may take 1-2 minutes.
{% endtab %}
{% endtabs %}

---

## 📄 Step 5: Create Environment File

We'll store sensitive data (API keys) in a `.env` file. Create it now as a placeholder:

```bash
cat > .env << 'EOF'
# GitHub Models (we'll fill this in Phase 2)
GITHUB_TOKEN=your_github_token_here

# WeatherAPI (we'll fill this in Phase 5)
WEATHER_API_KEY=your_weather_api_key_here
EOF
```

### 🔒 Security Note

The `.env` file should **never** be committed to git. Let's create a `.gitignore`:

```bash
cat > .gitignore << 'EOF'
# Virtual environment
.venv/
venv/

# Environment variables (secrets!)
.env

# Python cache
__pycache__/
*.pyc

# Chainlit files
.chainlit/
EOF
```

---

## 🗂️ Current Project Structure

Your project should now look like this:

```
langchain-chainlit-workshop/
├── .venv/              # Virtual environment (hidden folder)
├── .env                # Environment variables (we'll fill later)
├── .gitignore          # Git ignore rules
└── requirements.txt    # Python dependencies
```

---

## ✅ Checkpoint: Environment Ready

Let's verify everything is set up correctly:

### Test 1: Virtual Environment Active
```bash
which python
# Should show: /path/to/langchain-chainlit-workshop/.venv/bin/python
```

On Windows:
```powershell
where python
# Should show path containing .venv
```

### Test 2: Packages Installed
```bash
python -c "import chainlit; print(f'Chainlit version: {chainlit.__version__}')"
python -c "import langchain; print(f'LangChain version: {langchain.__version__}')"
```

**Expected output**:
```
Chainlit version: 2.x.x
LangChain version: 0.3.x
```

### Test 3: Environment File Exists
```bash
cat .env
# Should show the template with placeholder values
```

### ✨ All Tests Pass?

**Great job!** Your development environment is ready.

👉 **Next up: [Phase 2: GitHub Models Configuration](02-github-models.md)**

---

## ❓ Common Issues

### "uv: command not found"
Use pip instead:
```bash
python3 -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### "No module named chainlit"
Make sure your virtual environment is activated. You should see `(.venv)` in your prompt.

### Installation is very slow
- Check your internet connection
- Try using uv for faster installs
- If behind a corporate proxy, you may need to configure pip

### "Permission denied" errors
- Don't use `sudo` with pip in a virtual environment
- Make sure you activated the virtual environment first
