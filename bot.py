import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from extractor import extract_course_to_file

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Use /course <batch_id> to get the file.")

async def course(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Usage: /course <batch_id>")
        return

    batch_id = context.args[0]
    m = await update.message.reply_text("⏳ Processing...")

    try:
        result = extract_course_to_file(batch_id)
        if result.startswith("Error"):
            await update.message.reply_text(result)
        else:
            with open(result, 'rb') as f:
                await context.bot.send_document(chat_id=update.effective_chat.id, document=f)
            os.remove(result)
    except Exception as e:
        await update.message.reply_text(f"❌ Bot Error: {e}")
    finally:
        await m.delete()

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("course", course))
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()
            
