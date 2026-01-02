import os
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

PROXY_URL = os.getenv("PROXY_URL")  # socks5://user:pass@ip:port

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is running on Heroku with Proxy!")

async def main():
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .proxy_url(PROXY_URL)
        .build()
    )

    app.add_handler(CommandHandler("start", start))

    print("🤖 Bot started...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
    
