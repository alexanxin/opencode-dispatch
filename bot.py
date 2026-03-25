#!/usr/bin/env python3
import os
import threading
import queue
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

load_dotenv()

OPENCODE_API_URL = os.getenv("OPENCODE_API_URL", "http://127.0.0.1:5050")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_CHAT_ID = os.getenv("TELEGRAM_ALLOWED_CHAT_ID")
SESSION_ID = None
message_queue = queue.Queue()
is_processing = False
current_task = "Idle"
processing_lock = threading.Lock()


def get_session():
    """Get or create a session."""
    global SESSION_ID
    if SESSION_ID:
        return SESSION_ID
    try:
        r = requests.get(f"{OPENCODE_API_URL}/session", timeout=10)
        if r.ok:
            sessions = r.json()
            if sessions:
                SESSION_ID = sessions[0]["id"]
                return SESSION_ID
    except Exception:
        pass
    try:
        r = requests.post(f"{OPENCODE_API_URL}/session", json={}, timeout=10)
        if r.ok:
            SESSION_ID = r.json()["id"]
            return SESSION_ID
    except Exception:
        pass
    return None


def send_to_opencode(message):
    """Send message to opencode and return response."""
    session_id = get_session()
    if not session_id:
        return "Error: Could not connect to opencode session."

    try:
        r = requests.post(
            f"{OPENCODE_API_URL}/session/{session_id}/message",
            json={"parts": [{"type": "text", "text": f"[Telegram] {message}"}]},
            timeout=1200,
        )
        if r.ok:
            data = r.json()
            parts = data.get("parts", [])
            text_parts = [
                p["text"] for p in parts if p.get("type") == "text" and p.get("text")
            ]
            return (
                "\n".join(text_parts)
                if text_parts
                else "Message sent, no text response."
            )
        else:
            return f"opencode returned {r.status_code}: {r.text[:200]}"
    except requests.exceptions.ConnectionError:
        return "Can't connect to opencode. Is it running?"
    except requests.exceptions.Timeout:
        return "opencode took too long to respond. Please try again."
    except Exception as e:
        return f"Error: {str(e)}"


def process_queue(bot, chat_id):
    """Process messages in the queue one at a time."""
    global is_processing
    while True:
        try:
            item = message_queue.get(timeout=1)
            if item is None:
                break
            user_id, message_id, user_message = item
            with processing_lock:
                is_processing = True
            try:
                reply = send_to_opencode(user_message)

                async def send_reply():
                    await bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text=f"🔄 Processing...\n\n{reply[:4000]}",
                    )

                import asyncio

                asyncio.run(send_reply())
            finally:
                with processing_lock:
                    is_processing = False
            message_queue.task_done()
        except queue.Empty:
            continue


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "opencode-dispatch bot\n\n"
        "Send any message and opencode will process it.\n"
        f"Server: {OPENCODE_API_URL}"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "How to use:\n\n"
        "1. Make sure opencode is running\n"
        "2. Send me any message\n"
        "3. I'll forward it to opencode and relay the response\n\n"
        "Commands: /start, /help, /status, /working, /clear"
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session_id = get_session()
    try:
        r = requests.get(f"{OPENCODE_API_URL}/global/health", timeout=5)
        healthy = r.ok
    except Exception:
        healthy = False
    queue_size = message_queue.qsize()
    await update.message.reply_text(
        f"Server: {OPENCODE_API_URL}\n"
        f"opencode: {'✅' if healthy else '❌'}\n"
        f"Session: {session_id or 'none'}\n"
        f"Queue: {queue_size} messages"
    )


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with processing_lock:
        if is_processing:
            await update.message.reply_text(
                "❌ Can't clear queue while processing. Wait for current task to finish."
            )
        else:
            while not message_queue.empty():
                try:
                    message_queue.get_nowait()
                except queue.Empty:
                    break
            await update.message.reply_text("✅ Queue cleared.")


async def working_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_task
    if is_processing:
        await update.message.reply_text(
            f'🔄 Currently working on:\n"{current_task}"\n\nQueue: {message_queue.qsize()} messages'
        )
    else:
        await update.message.reply_text("✅ Currently idle. No task in progress.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_processing, current_task
    chat_id = str(update.message.chat.id)
    if ALLOWED_CHAT_ID and chat_id != ALLOWED_CHAT_ID:
        await update.message.reply_text(
            "❌ This bot is not authorized to respond to you."
        )
        return
    user_message = update.message.text
    user_id = update.effective_user.id if update.effective_user else "unknown"

    with processing_lock:
        currently_processing = is_processing

    if currently_processing:
        sent = await update.message.reply_text(
            "⏳ opencode is busy. Your message has been added to the queue.\n"
            "I'll respond when ready. Use /status to check queue position."
        )
        message_queue.put((user_id, sent.message_id, user_message))
    else:
        current_task = (
            user_message[:50] + "..." if len(user_message) > 50 else user_message
        )
        await update.message.chat.send_action("typing")
        sent = await update.message.reply_text("🔄 Processing...")
        with processing_lock:
            is_processing = True
        try:
            reply = send_to_opencode(user_message)
            await sent.edit_text(reply[:4000])
        except Exception as e:
            await sent.edit_text(f"Error: {str(e)}")
        finally:
            with processing_lock:
                is_processing = False
            current_task = "Idle"


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.chat.id)
    if ALLOWED_CHAT_ID and chat_id != ALLOWED_CHAT_ID:
        return
    await update.message.reply_text("Voice messages not yet supported. Send text.")


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.chat.id)
    if ALLOWED_CHAT_ID and chat_id != ALLOWED_CHAT_ID:
        return
    await update.message.reply_text("File handling not yet supported. Send text.")


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.chat.id)
    if ALLOWED_CHAT_ID and chat_id != ALLOWED_CHAT_ID:
        return
    await update.message.reply_text("Image handling not yet supported. Send text.")


def main():
    if not BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not set in .env file")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("working", working_command))
    app.add_handler(CommandHandler("clear", clear_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print(f"opencode-dispatch bot starting...")
    print(f"Connecting to opencode at: {OPENCODE_API_URL}")
    print("Press Ctrl+C to stop")

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
