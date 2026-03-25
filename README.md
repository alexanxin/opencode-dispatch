<p align="center">
  <h1> opencode-dispatch</h1>
</p>

<p align="center">
  <strong>Control opencode from Telegram — like Claude's Dispatch, but for opencode.</strong>
</p>

<p align="center">
  <a href="https://github.com/alexanxin/opencode-dispatch"><img src="https://img.shields.io/github/stars/alexanxin/opencode-dispatch?style=for-the-badge" alt="GitHub Stars"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="MIT License"></a>
  <a href="https://opencode.ai"><img src="https://img.shields.io/badge/opencode-CLI-orange?style=for-the-badge" alt="opencode"></a>
</p>

<p align="center">
  <a href="#quick-setup">Setup</a> · <a href="#how-it-works">How It Works</a> · <a href="#use-cases">Use Cases</a> · <a href="#security">Security</a> · <a href="#troubleshooting">Troubleshooting</a>
</p>

---

> I deeply appreciate what the opencode team is building. This is my small contribution to their already awesome work — making opencode accessible from anywhere via Telegram.

Bridge your Telegram bot to the [opencode CLI](https://opencode.ai). Send messages from your phone, opencode processes them just like it would in a terminal. Perfect for when you're away from your desk but still want AI assistance.

## What You Need

- **[opencode CLI](https://opencode.ai)** installed — verify with `opencode --version`
- A Telegram account
- Python 3.10+ or Node.js
- A Telegram bot token (free from [@BotFather](https://t.me/BotFather))

## Quick Setup

### Step 1: Create a Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Give it a name (e.g., "My opencode Bot")
4. Give it a username ending in `bot` (e.g., `my_opencode_bot`)
5. Copy the token BotFather gives you

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

**Python:**
```bash
python bot.py
```

**Node.js:**
```bash
npm start
```

### Step 6: Chat

Open Telegram, find your bot, and send a message. opencode will receive it and respond through the bot.

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and server info |
| `/help` | Usage instructions |
| `/status` | Server health, session ID, queue size |
| `/working` | Check what task is currently being processed |
| `/clear` | Clear pending messages from queue |

## How It Works

```
Your Phone → Telegram → bot.py → opencode API (port 5050) → response → Telegram → Your Phone
```

1. You send a message to your Telegram bot
2. The bot forwards it to opencode via the server API
3. opencode processes it in your project context
4. The response comes back through the bot to your phone

## Use Cases

### 1. Ask About Your Codebase

```
You: "What does the auth middleware in @middleware.ts do?"
opencode: "The auth middleware checks for a valid JWT token
           in the Authorization header. It extracts the user ID
           and attaches it to the request object."
```

### 2. Start a Task

```
You: "Add input validation to the signup form"
opencode: "I'll add validation to the signup form. I found the form in
           src/components/Signup.tsx. I'll add email format validation,
           password length requirements, and field presence checks."
```

### 3. Check Project Status

```
You: "Are there any failing tests?"
opencode: "I ran the test suite. 47 passing, 2 failing:
           - test_checkout_flow: assertion error in calculateTotal
           - test_user_profile: timeout waiting for API response"
```

### 4. Get Commit Summaries

```
You: "What changed in the last 3 commits?"
opencode: "Last 3 commits:
           1. Add user profile API endpoints (2 files changed)
           2. Fix payment timeout issue (1 file changed)
           3. Update test fixtures for new schema (4 files changed)"
```

### 5. Quick Lookups

```
You: "What environment variables does this project need?"
opencode: "Required env vars from .env.example:
           - DATABASE_URL: PostgreSQL connection string
           - JWT_SECRET: Secret for token signing
           - STRIPE_KEY: Stripe API key for payments"
```

## Security

### Limit workspace access

Always start opencode from a specific project folder:

```bash
cd ~/my-project        # Only this folder and subfolders
opencode serve --port 5050
```

**Never** run from your home directory (`~`) or root (`/`). opencode can access all files in the directory it's started from.

### Password protect (recommended)

Set a password to prevent unauthorized local access:

```bash
OPENCODE_SERVER_PASSWORD=your-secret opencode serve --port 5050
```

Add to `.env`:
```env
OPENCODE_SERVER_PASSWORD=your-secret
```

### Network safety

The server only listens on `127.0.0.1` (localhost) by default. It's not accessible from other machines on your network. Never use `--hostname 0.0.0.0` unless you know what you're doing.

## Troubleshooting

**"Can't connect to opencode"**
- Make sure `opencode serve --port 5050` is running in a terminal
- Verify with: `curl http://127.0.0.1:5050/global/health`

**"Bot isn't responding"**
- Check your Telegram bot token in `.env`
- Make sure the bot is running (`python bot.py` or `npm start`)

**"Port already in use"**
- Another process is using port 5050
- Pick a different port: `opencode serve --port 5051`
- Update `OPENCODE_API_URL` in `.env` to match

**"opencode command not found"**
- Install the CLI: `curl -fsSL https://opencode.ai/install | bash`
- Then restart your terminal or run: `source ~/.zshrc`

## Tips for Best Results

- **Be specific**: Instead of "fix my code," say "fix the null pointer error in UserService.java"
- **One task at a time**: For complex requests, break them into smaller steps
- **Keep context**: Mention relevant files or features so opencode understands what you're referring to
- **Use /status**: Check if opencode is healthy before sending important tasks

## Contributing

Found a bug? Have an improvement? Open an issue or submit a pull request!

## License

MIT
