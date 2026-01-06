# Troubleshooting Guide

> Common issues and their solutions for the workshop

---

## 🐍 Python & Environment Issues

### "python: command not found" or "python3: command not found"

**Problem**: Python is not installed or not in your PATH.

**Solutions**:
- **macOS**: Install with Homebrew: `brew install python@3.12`
- **Windows**: Download from [python.org](https://www.python.org/downloads/). During installation, check "Add Python to PATH"
- **Linux**: `sudo apt install python3.12` (Ubuntu/Debian) or `sudo dnf install python3.12` (Fedora)

### "No module named 'xxx'"

**Problem**: Package not installed or virtual environment not activated.

**Solutions**:
1. Make sure your virtual environment is activated:
   ```bash
   source .venv/bin/activate  # macOS/Linux
   .venv\Scripts\activate     # Windows
   ```
2. Install missing package:
   ```bash
   pip install package_name
   # or reinstall all
   pip install -r requirements.txt
   ```

### "Permission denied" when installing packages

**Problem**: Trying to install system-wide without sudo.

**Solution**: Always use a virtual environment. Never use `sudo pip install`.

---

## 🔑 Authentication Issues

### "401 Unauthorized" with GitHub Models

**Problem**: Invalid or missing GitHub token.

**Solutions**:
1. Check your `.env` file has the correct token:
   ```
   GITHUB_TOKEN=ghp_xxxxxxxxxxxx
   ```
2. Verify the token hasn't expired (check [github.com/settings/tokens](https://github.com/settings/tokens))
3. Generate a new token if needed
4. Restart the Chainlit server after changing `.env`

### "API key not valid" with WeatherAPI

**Problem**: Invalid WeatherAPI key.

**Solutions**:
1. Log into [weatherapi.com](https://www.weatherapi.com/)
2. Go to Dashboard → Your API Key
3. Copy the key and update `.env`:
   ```
   WEATHER_API_KEY=your_actual_key
   ```
4. Regenerate the key if needed

---

## 🌐 Network Issues

### "Connection refused" or "Cannot connect to server"

**Problem**: Chainlit server not running or wrong port.

**Solutions**:
1. Make sure Chainlit is running: `chainlit run app.py -w`
2. Check the terminal for the correct URL (usually http://localhost:8000)
3. Check if another process is using port 8000:
   ```bash
   lsof -i :8000  # macOS/Linux
   netstat -ano | findstr :8000  # Windows
   ```
4. Try a different port: `chainlit run app.py -w --port 8080`

### "Timeout" errors when calling APIs

**Problem**: Slow network or API rate limits.

**Solutions**:
1. Check your internet connection
2. Wait a minute (may be rate limited)
3. Try a different city for weather
4. Increase timeout in code:
   ```python
   timeout=30.0  # instead of 10.0
   ```

---

## 💬 Chainlit Issues

### Chat UI loads but messages don't appear

**Problem**: WebSocket connection issues.

**Solutions**:
1. Hard refresh the browser (Ctrl+Shift+R or Cmd+Shift+R)
2. Clear browser cache
3. Try a different browser
4. Check browser console (F12) for errors

### "Session not found" errors

**Problem**: Session expired or server restarted.

**Solutions**:
1. Refresh the browser page
2. Session data is lost when server restarts - this is normal during development

### Streaming doesn't work (text appears all at once)

**Problem**: Streaming not properly configured.

**Solutions**:
1. Make sure `streaming=True` in ChatOpenAI:
   ```python
   llm = ChatOpenAI(streaming=True, ...)
   ```
2. Use `astream()` not `invoke()`:
   ```python
   async for chunk in llm.astream(messages):
   ```
3. Use `stream_token()` for real-time display:
   ```python
   await msg.stream_token(chunk.content)
   ```

---

## 🔧 Tool Calling Issues

### Agent never calls tools

**Problem**: Tool not properly registered or prompt unclear.

**Solutions**:
1. Verify tools are passed to the agent:
   ```python
   agent = create_tool_calling_agent(llm, TOOLS, prompt)
   ```
2. Check console output (set `verbose=True` in AgentExecutor)
3. Make tool descriptions clear and specific
4. Verify the model supports tool calling (gpt-4o-mini does)

### Tool is called but returns empty

**Problem**: Tool function not returning properly.

**Solutions**:
1. Ensure tool function returns a string
2. Check for exceptions in the tool (add try/except)
3. Verify API responses are being parsed correctly
4. Test the tool directly:
   ```python
   from tools import get_weather
   print(get_weather("London"))
   ```

### "Tool not found" errors

**Problem**: Import or configuration issue.

**Solutions**:
1. Check the import works:
   ```python
   from tools import TOOLS
   print(TOOLS)
   ```
2. Ensure `tools.py` is in the same directory
3. Check for syntax errors in `tools.py`

---

## 🖥️ Platform-Specific Issues

### Windows: "execution of scripts is disabled"

**Problem**: PowerShell execution policy.

**Solution**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Windows: Unicode/Emoji display issues

**Problem**: Terminal doesn't support Unicode.

**Solutions**:
1. Use Windows Terminal instead of CMD
2. Set UTF-8 encoding: `chcp 65001`
3. Remove emojis from output if needed

### macOS: "SSL certificate verify failed"

**Problem**: Certificate issues.

**Solutions**:
1. Install certificates:
   ```bash
   /Applications/Python\ 3.x/Install\ Certificates.command
   ```
2. Or reinstall Python with `brew install python@3.12`

---

## 📊 Rate Limits

### GitHub Models rate limits

**Free tier limits**:
- Requests per minute: ~15-20
- Tokens per minute: ~150,000

**Solutions**:
1. Wait a minute between heavy requests
2. Use `gpt-4o-mini` instead of `gpt-4o` (faster, lower limits)
3. Workshop facilitators: prepare backup tokens

### WeatherAPI rate limits

**Free tier limits**:
- 1,000,000 calls per month
- Usually not an issue for workshops

---

## 🆘 Still Stuck?

### Debug Steps

1. **Check the terminal** for error messages
2. **Read the full error** - the answer is often in the traceback
3. **Simplify** - go back to a working version and add changes one at a time
4. **Print debug info**:
   ```python
   print(f"Token: {os.getenv('GITHUB_TOKEN')[:10]}...")
   print(f"Weather key set: {bool(os.getenv('WEATHER_API_KEY'))}")
   ```

### Get Help

- **Workshop facilitator** - They're here to help!
- **Pair with a neighbor** - Fresh eyes help
- **Solution files** - Check `solutions/` folder for working code

---

## 🔄 Quick Fixes Checklist

When something breaks, try these in order:

- [ ] Virtual environment activated? (`(.venv)` in prompt)
- [ ] All packages installed? (`pip install -r requirements.txt`)
- [ ] `.env` file has correct values?
- [ ] Server running? (`chainlit run app.py -w`)
- [ ] Browser refreshed?
- [ ] Terminal shows any errors?
- [ ] Internet connection working?
