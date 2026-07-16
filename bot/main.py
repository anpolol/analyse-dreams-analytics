import logging
from telegram.ext import ApplicationBuilder, MessageHandler, filters
import os

BOT_TOKEN = os.environ["BOT_TOKEN"]
PROXY_URL = os.environ.get("PROXY_URL")

# Set before importing anything that builds an HTTP client (openai, langfuse, ...)
# so libraries relying on httpx/requests trust_env pick up the proxy too —
# python-telegram-bot is the one exception, wired explicitly below.
if PROXY_URL:
    os.environ["HTTP_PROXY"] = PROXY_URL
    os.environ["HTTPS_PROXY"] = PROXY_URL
    os.environ["http_proxy"] = PROXY_URL
    os.environ["https_proxy"] = PROXY_URL

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
