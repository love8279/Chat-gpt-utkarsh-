import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from extractor import extract_course_to_file

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome!\nUse /course <batch_id> to extract course videos.")

async def course(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Usage: /course <batch_id>")
        return

    batch_id = context.args[0]
    status_msg = await update.message.reply_text("⏳ Extracting... Please wait.")

    try:
        # File generate karna
        result = extract_course_to_file(batch_id)
        
        if result.startswith("Error"):
            await update.message.reply_text(f"❌ {result}")
        else:
            # File ko Telegram par send karna
            with open(result, 'rb') as doc:
                await context.bot.send_document(
                    chat_id=update.effective_chat.id, 
                    document=doc,
                    caption=f"✅ Done! Batch ID: {batch_id}"
                )
            # Kaam hone ke baad temporary file delete karna
            if os.path.exists(result):
                os.remove(result)
    except Exception as e:
        await update.message.reply_text(f"❌ System Error: {str(e)}")
    finally:
        await status_msg.delete()

def main():
    if not BOT_TOKEN:
        print("BOT_TOKEN not found!")
        return
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("course", course))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
