
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from extractor import extract_course_to_file


BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome!\nUse /course <batch_id> to extract course.")

async def course(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Usage: /course <batch_id>")
        return

    batch_id = context.args[0]
    await update.message.reply_text("⏳ Extracting course, please wait...")

    try:
        result = extract_course_to_file(
            batch_id)
        await update.message.reply_text(result[:4000])
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("course", course))
    app.run_polling()

if __name__ == "__main__":
    main()
    
