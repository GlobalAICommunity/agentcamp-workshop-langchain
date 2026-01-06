# Prerequisites

> ⏱️ **Time to complete**: 5 minutes (or done before the workshop)

Before we dive into building our AI chat agent, let's make sure you have everything ready. This phase is a quick check to ensure a smooth workshop experience.

---

## 🎒 What You Need

### 1. **A Computer with Terminal Access**

| OS | Terminal |
|----|----------|
| macOS | Terminal.app or iTerm2 |
| Windows | PowerShell, CMD, or Windows Terminal |
| Linux | Any terminal emulator |

### 2. **Python 3.10 or Higher**

Check your Python version:

```bash
python3 --version
# or on Windows:
python --version
```

**Expected output**: `Python 3.10.x` or higher (3.11, 3.12, 3.13 are all fine)

{% hint style="info" %}
**Don't have Python?** 
- macOS: `brew install python@3.12`
- Windows: Download from [python.org](https://www.python.org/downloads/)
- Linux: `sudo apt install python3.12` (Ubuntu/Debian)
{% endhint %}

### 3. **Git Installed**

```bash
git --version
```

**Expected output**: `git version 2.x.x`

### 4. **A Code Editor**

We recommend **Visual Studio Code** with the Python extension, but any editor works.

### 5. **A GitHub Account**

You'll need this to access GitHub Models (free LLM API). 

👉 No account? Create one at [github.com](https://github.com/signup)

### 6. **Internet Connection**

Required for:
- Downloading packages
- Calling GitHub Models API
- Calling WeatherAPI

---

## 📋 Pre-Workshop Checklist

Run through this checklist. You should be able to check all boxes:

- [ ] Python 3.10+ installed and accessible from terminal
- [ ] Git installed
- [ ] GitHub account created and you can log in
- [ ] Code editor ready (VS Code recommended)
- [ ] Stable internet connection

---

## 🔑 Accounts to Create (If You Haven't Already)

### GitHub Account
If you don't have one:
1. Go to [github.com/signup](https://github.com/signup)
2. Follow the registration process
3. Verify your email address

### WeatherAPI Account (Free)
We'll use this for the tool-calling demo:
1. Go to [weatherapi.com](https://www.weatherapi.com/)
2. Click "Sign Up" (top right)
3. Choose the **Free** plan
4. You'll get an API key after email verification

{% hint style="warning" %}
**Save your WeatherAPI key!** You'll need it in Phase 5.
{% endhint %}

---

## 💻 Optional but Recommended

### uv (Fast Python Package Manager)

We'll use `uv` for faster dependency installation. It's optional but makes things much faster:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Verify installation:
```bash
uv --version
```

If you don't want to install `uv`, that's fine - we'll provide `pip` alternatives for every command.

---

## ✅ Checkpoint: Prerequisites Complete

Before moving on, verify:

| Check | Command | Expected |
|-------|---------|----------|
| Python | `python3 --version` | 3.10+ |
| Git | `git --version` | 2.x.x |
| GitHub | Log into github.com | Success |
| WeatherAPI | Check email for API key | Have the key |

### 🎉 All Green?

**Excellent!** You're ready for the workshop. 

👉 **Next up: [Phase 1: Environment Setup](01-environment.md)**

---

## ❓ Common Issues

### "python3: command not found"
- Windows: Try `python` instead of `python3`
- macOS: Install via `brew install python@3.12`
- Make sure Python is in your PATH

### "I forgot my WeatherAPI key"
- Log into [weatherapi.com](https://www.weatherapi.com/)
- Go to Dashboard → Your API Key
- You can regenerate it if needed

### "I can't create a GitHub account"
- Ask the workshop facilitator for a shared demo token
- You can pair with someone who has an account
