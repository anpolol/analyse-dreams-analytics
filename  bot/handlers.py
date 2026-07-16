import os

from telegram import Update
from telegram import ReplyKeyboardMarkup, KeyboardButton

from telegram.ext import ContextTypes
from LangGraph import react_graph
from langchain_core.messages import HumanMessage
from langfuse.langchain import CallbackHandler

ALLOWED_USER_ID = int(os.environ["ALLOWED_USER_ID"])

langfuse_handler = CallbackHandler()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("Нет доступа.")
        return

    user_text = update.message.text
    KEYBOARD = ReplyKeyboardMarkup(
    [
        [KeyboardButton("/start")],
    ],
    resize_keyboard=True  # кнопки компактного размера
)

    if user_text == "/start":
        context.user_data["history"] = [] 
        await update.message.reply_text("Привет! История сбросилась, спрашивай что интересно узнать по базе analysedreams.com", reply_markup=KEYBOARD)
    else:
        history = context.user_data.get("history", [])[-50:] + [HumanMessage(content=user_text)]
        result  = react_graph.invoke({
        "user_input": user_text,
        "database_schema": "",
        "messages": history
        },
        config={"callbacks": [langfuse_handler]})
        answer = result["messages"][-1].content
        limit = 4096
        context.user_data["history"] = result["messages"]
        await update.message.reply_text(answer[:limit], reply_markup=KEYBOARD)            
