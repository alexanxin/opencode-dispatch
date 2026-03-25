# Beyond the Terminal: The Road to a Truly Autonomous AI Agent

**opencode-dispatch** is a secure Telegram bridge for the [opencode CLI](https://opencode.ai). It brings the power of a 120K-star, self-hosted AI agent to your pocket—giving you "Dispatch-style" remote access without the corporate subscription or vendor lock-in.

<p align="center">
  <img src="https://pbs.twimg.com/media/HEREOD6WcAAaG7_?format=jpg&name=4096x4096" alt="opencode-dispatch Cover" width="700">
</p>

<p align="center">
  <a href="https://github.com/alexanxin/opencode-dispatch"><img src="https://img.shields.io/github/stars/alexanxin/opencode-dispatch?style=for-the-badge" alt="GitHub Stars"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="MIT License"></a>
  <a href="https://opencode.ai"><img src="https://img.shields.io/badge/opencode-CLI-orange?style=for-the-badge" alt="opencode"></a>
</p>

---

## Why opencode-dispatch?

While the industry moves toward closed, subscription-based mobile interfaces, **opencode-dispatch** stays true to the open-source ethos: **Your models, your hardware, your data.**

- **📱 Remote Autonomy:** Manage codebases, run tests, and refactor files from a Telegram chat.
- **🤖 Model Agnostic:** Connect to 75+ providers via Models.dev or run entirely local via Ollama.
- **🔒 Security First:** Built-in Telegram Chat ID locking and context isolation.
- **⚡ Lightweight:** Runs on a $5 VPS or your local machine with minimal overhead.

## The Vision: Building "OpenClaw"

This repository is more than a bridge; it's a foundational layer for a persistent, autonomous agent ecosystem. We are moving beyond stateless terminal commands toward an agent that:

1. **Remembers:** Persistent cross-session context.
2. **Acts:** Scheduled task execution and background monitoring.
3. **Learns:** A plug-and-play skills and personality registry.

---

## What You Need

- **[opencode CLI](https://opencode.ai)** installed — verify with `opencode --version`
- A Telegram account
- Python 3.10+ or Node.js
- A Telegram bot token (free from [@BotFather](https://t.me/BotFather))

## Quick Setup

### Step 1: Create a Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` and follow the prompts to get your **token**.

### Step 2: Install Dependencies

Choose Python or Node.js (both work the same):

**Python:**
```bash
pip install -r requirements.txt
```

**Node.js:**
```bash
npm install
```

### Step 3: Configure

```bash
cp .env.example .env
```

Edit `.env` and add your Telegram bot token:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
OPENCODE_API_URL=http://127.0.0.1:5050
```

### Step 4: Start opencode

```bash
cd ~/your-project
opencode serve --port 5050
```

> **Important:** Always `cd` into a specific project folder first. This limits opencode's access to that folder and its subfolders.

### Step 5: Run the Bot

- **Python:** `python bot.py`
- **Node.js:** `npm start`

### Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and server info |
| `/status` | Server health, session ID, queue size |
| `/working` | Check what task is currently being processed |
| `/clear` | Clear pending messages from queue |

## Security Recommendations

### 1. Limit workspace access

Never run from your home directory (`~`) or root (`/`). opencode can access all files in the directory it's started from.

### 2. Password protect (Recommended)

Set a password to prevent unauthorized local access:

```bash
OPENCODE_SERVER_PASSWORD=your-secret opencode serve --port 5050
```

Then add to `.env`:

```env
OPENCODE_SERVER_PASSWORD=your-secret
```

### 3. Restrict to your Telegram account (Highly Recommended)

To lock the bot so only YOU can use it:

1. Get your chat ID from [@userinfobot](https://t.me/userinfobot)
2. Add to `.env`:

```env
TELEGRAM_ALLOWED_CHAT_ID=your_chat_id_here
```

## Troubleshooting

**"Can't connect to opencode"**
- Make sure `opencode serve --port 5050` is running in a terminal
- Verify with: `curl http://127.0.0.1:5050/global/health`

**"Bot isn't responding"**
- Check your Telegram bot token in `.env`
- Make sure the bot is running (`python bot.py` or `npm start`)

**"Port already in use"**
- Pick a different port: `opencode serve --port 5051`
- Update `OPENCODE_API_URL` in `.env` to match

**"opencode command not found"**
- Install: `curl -fsSL https://opencode.ai/install | bash`
- Then run: `source ~/.zshrc`

## Contributing

Found a bug? Have an improvement? Open an issue or submit a pull request!

## License

MIT
