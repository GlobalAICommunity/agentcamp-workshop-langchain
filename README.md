# 🤖 Building AI Chat Agents with LangChain, Chainlit & GitHub Models

> **A 90-minute hands-on workshop for tech conferences**

Welcome to this practical workshop where you'll build a fully functional AI chat agent from scratch! By the end of this session, you'll have created an intelligent assistant that can have conversations, call external tools (like fetching weather data), and integrate with the Model Context Protocol (MCP).

---

## 🎯 What You'll Build

A conversational AI agent with:
- **Real-time chat interface** powered by Chainlit
- **LLM backbone** using GitHub Models (completely free!)
- **Tool calling** capabilities (weather API integration)
- **MCP integration** for extensible agent capabilities

![Workshop Overview](./assets/overview.png)

---

## 📚 Workshop Structure

| Phase | Duration | Topic |
|-------|----------|-------|
| **0** | 5 min | Prerequisites & Setup Check |
| **1** | 10 min | Environment Setup |
| **2** | 10 min | GitHub Models Configuration |
| **3** | 15 min | Your First Chainlit Chat App |
| **4** | 15 min | Adding LangChain for LLM Power |
| **5** | 20 min | Tool Calling with Weather API |
| **6** | 15 min | MCP Integration |

Each phase ends with a **✅ Checkpoint** where you'll verify everything works before moving on.

---

## 🛠️ Tech Stack

| Technology | Purpose | Version |
|------------|---------|---------|
| Python | Runtime | 3.10+ |
| Chainlit | Chat UI Framework | 2.x |
| LangChain | LLM Orchestration | 0.3.x |
| GitHub Models | Free LLM API | Latest |
| WeatherAPI | Tool Demo | Free Tier |
| MCP | Agent Protocol | 1.x |

---

## 🚀 Quick Start

```bash
# Clone or create the workshop folder
mkdir langchain-chainlit-workshop
cd langchain-chainlit-workshop

# Follow the phases in order starting from:
# 📖 docs/00-prerequisites.md
```

---

## 📁 Project Structure

```
langchain-chainlit-workshop/
├── README.md                 # You are here
├── SUMMARY.md               # GitBook navigation
├── docs/
│   ├── 00-prerequisites.md  # What you need before starting
│   ├── 01-environment.md    # Python & dependencies setup
│   ├── 02-github-models.md  # Getting your free API access
│   ├── 03-chainlit-basics.md # First chat application
│   ├── 04-langchain.md      # LLM integration
│   ├── 05-tool-calling.md   # Weather API tools
│   └── 06-mcp-integration.md # MCP setup
├── solutions/               # Complete code for each phase
│   ├── phase-03/
│   ├── phase-04/
│   ├── phase-05/
│   └── phase-06/
└── assets/                  # Images and diagrams
```

---

## 👨‍🏫 For Workshop Facilitators

### Before the Workshop
1. Ensure attendees have received the prerequisites checklist
2. Have backup GitHub tokens ready for attendees who forgot
3. Test the WeatherAPI endpoint is responding
4. Prepare a hotspot/backup internet option

### During the Workshop
- Each phase has a checkpoint - don't proceed until 80%+ have passed
- The `solutions/` folder contains working code for each phase
- Common issues are documented at the end of each phase

---

## 📝 License

This workshop material is provided under the MIT License. Feel free to use, modify, and distribute for your own workshops and training sessions.

---

**Ready to start? Head to [Prerequisites](docs/00-prerequisites.md)! 👉**
