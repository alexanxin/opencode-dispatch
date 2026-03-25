import { Telegraf } from 'telegraf';
import { config } from 'dotenv';
import axios from 'axios';

config();

const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const OPENCODE_API_URL = process.env.OPENCODE_API_URL || 'http://127.0.0.1:5050';
const ALLOWED_CHAT_ID = process.env.TELEGRAM_ALLOWED_CHAT_ID ? String(process.env.TELEGRAM_ALLOWED_CHAT_ID) : null;
const messageQueue = [];
let isProcessing = false;
let currentTask = 'Idle';

if (!BOT_TOKEN) {
    console.error('Error: TELEGRAM_BOT_TOKEN not set in .env file');
    process.exit(1);
}

async function getSession() {
    try {
        const r = await axios.get(`${OPENCODE_API_URL}/session`, { timeout: 10000 });
        if (r.data && r.data.length > 0) {
            return r.data[0].id;
        }
    } catch (e) {}
    try {
        const r = await axios.post(`${OPENCODE_API_URL}/session`, {}, { timeout: 10000 });
        if (r.data && r.data.id) {
            return r.data.id;
        }
    } catch (e) {}
    return null;
}

async function sendToOpencode(message) {
    const sessionId = await getSession();
    if (!sessionId) {
        return "Error: Could not connect to opencode session.";
    }

    try {
        const r = await axios.post(
            `${OPENCODE_API_URL}/session/${sessionId}/message`,
            { parts: [{ type: "text", text: `[Telegram] ${message}` }] },
            { timeout: 1200000 }
        );
        if (r.data && r.data.parts) {
            const textParts = r.data.parts
                .filter(p => p.type === "text" && p.text)
                .map(p => p.text);
            return textParts.join("\n") || "Message sent, no text response.";
        }
        return "Message sent.";
    } catch (error) {
        if (error.code === 'ECONNREFUSED') {
            return "Can't connect to opencode. Is it running?";
        } else if (error.code === 'ETIMEDOUT') {
            return "opencode took too long to respond. Please try again.";
        }
        return `Error: ${error.message}`;
    }
}

async function processQueue() {
    while (messageQueue.length > 0) {
        const item = messageQueue.shift();
        isProcessing = true;
        try {
            const reply = await sendToOpencode(item.message);
            await item.ctx.telegram.editMessageText(
                item.chatId,
                item.messageId,
                null,
                `🔄 Processed from queue\n\n${reply.substring(0, 4000)}`
            );
        } catch (e) {
            await item.ctx.telegram.editMessageText(
                item.chatId,
                item.messageId,
                null,
                `Error: ${e.message}`
            );
        }
        isProcessing = false;
    }
}

const bot = new Telegraf(BOT_TOKEN);

bot.start((ctx) => {
    ctx.reply(
        'opencode-dispatch bot\n\n' +
        'Send any message and opencode will process it.\n' +
        `Server: ${OPENCODE_API_URL}`
    );
});

bot.help((ctx) => {
    ctx.reply(
        'How to use:\n\n' +
        '1. Make sure opencode is running\n' +
        '2. Send me any message\n' +
        '3. I\'ll forward it to opencode and relay the response\n\n' +
        'Commands: /start, /help, /status, /working, /clear'
    );
});

bot.command('status', async (ctx) => {
    const sessionId = await getSession();
    let healthy = false;
    try {
        const r = await axios.get(`${OPENCODE_API_URL}/global/health`, { timeout: 5000 });
        healthy = r.ok;
    } catch (e) {}
    ctx.reply(
        `Server: ${OPENCODE_API_URL}\n` +
        `opencode: ${healthy ? '✅' : '❌'}\n` +
        `Session: ${sessionId || 'none'}\n` +
        `Queue: ${messageQueue.length} messages`
    );
});

bot.command('clear', (ctx) => {
    if (isProcessing) {
        ctx.reply('❌ Can\'t clear queue while processing. Wait for current task to finish.');
    } else {
        messageQueue.length = 0;
        ctx.reply('✅ Queue cleared.');
    }
});

bot.command('working', (ctx) => {
    if (isProcessing) {
        ctx.reply(`🔄 Currently working on:\n"${currentTask}"\n\nQueue: ${messageQueue.length} messages`);
    } else {
        ctx.reply('✅ Currently idle. No task in progress.');
    }
});

bot.on('text', async (ctx) => {
    const chatId = String(ctx.chat.id);
    if (ALLOWED_CHAT_ID && chatId !== ALLOWED_CHAT_ID) {
        ctx.reply('❌ This bot is not authorized to respond to you.');
        return;
    }
    
    const userMessage = ctx.message.text;

    if (isProcessing) {
        const sent = await ctx.reply(
            '⏳ opencode is busy. Your message has been added to the queue.\n' +
            'I\'ll respond when ready. Use /status to check queue position.'
        );
        messageQueue.push({
            message: userMessage,
            chatId: ctx.chat.id,
            messageId: sent.message_id,
            ctx: ctx
        });
    } else {
        currentTask = userMessage.length > 50 ? userMessage.substring(0, 50) + '...' : userMessage;
        const sent = await ctx.reply('🔄 Processing...');
        isProcessing = true;
        try {
            const reply = await sendToOpencode(userMessage);
            await ctx.telegram.editMessageText(
                ctx.chat.id,
                sent.message_id,
                null,
                reply.substring(0, 4000)
            );
        } catch (e) {
            await ctx.telegram.editMessageText(
                ctx.chat.id,
                sent.message_id,
                null,
                `Error: ${e.message}`
            );
        }
        isProcessing = false;
        currentTask = 'Idle';
        
        if (messageQueue.length > 0) {
            processQueue();
        }
    }
});

bot.on('voice', (ctx) => {
    const chatId = String(ctx.chat.id);
    if (ALLOWED_CHAT_ID && chatId !== ALLOWED_CHAT_ID) return;
    ctx.reply('Voice messages not yet supported. Send text.');
});

bot.on('document', (ctx) => {
    const chatId = String(ctx.chat.id);
    if (ALLOWED_CHAT_ID && chatId !== ALLOWED_CHAT_ID) return;
    ctx.reply('File handling not yet supported. Send text.');
});

bot.on('photo', (ctx) => {
    const chatId = String(ctx.chat.id);
    if (ALLOWED_CHAT_ID && chatId !== ALLOWED_CHAT_ID) return;
    ctx.reply('Image handling not yet supported. Send text.');
});

console.log('opencode-dispatch bot starting...');
console.log(`Connecting to opencode at: ${OPENCODE_API_URL}`);
console.log('Press Ctrl+C to stop');

bot.launch();

process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));
