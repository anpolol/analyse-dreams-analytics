import logging
from telegram.ext import ApplicationBuilder, MessageHandler, filters
import os

BOT_TOKEN = os.environ["BOT_TOKEN"]
PROXY_URL = os.environ.get("PROXY_URL")

from handlers import handle_message


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

def main():
    builder = ApplicationBuilder().token(BOT_TOKEN)
    if PROXY_URL:
        builder = builder.proxy(PROXY_URL).get_updates_proxy(PROXY_URL)
    app = builder.build()
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    logging.info("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
