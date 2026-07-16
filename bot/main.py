import logging
from telegram.ext import ApplicationBuilder, MessageHandler, filters
import os

BOT_TOKEN = os.environ["BOT_TOKEN"]

from handlers import handle_message


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    logging.info("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
