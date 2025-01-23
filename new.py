import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.router import Router
from aiogram.filters import Command
from aiogram.types import Update
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse

from data import conf

WEBHOOK_URL = f"{conf.webhook.url}/webhook/{conf.bot_token.token}"
WEBHOOK_PATH = f"/webhook/{conf.bot_token.token}"
WEBAPP_HOST = conf.webhook.host
WEBAPP_PORT = conf.webhook.port

bot = Bot(token=conf.bot_token.token)
dp = Dispatcher()
router = Router()

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(f"Salom, {message.chat.first_name}! Bot ishlayapti.")


dp.include_router(router)


@app.on_event("startup")
async def on_startup():
    logger.info("Starting webhook setup")
    await bot.set_webhook(WEBHOOK_URL)
    logger.info("Webhook set at %s", WEBHOOK_URL)


@app.on_event("shutdown")
async def on_shutdown():
    logger.info("Shutting down bot")
    await bot.session.close()


@app.post(WEBHOOK_PATH)
async def webhook_handler(update: Update, background_tasks: BackgroundTasks):
    background_tasks.add_task(dp.feed_webhook_update, bot, update)
    return JSONResponse({"ok": True})


# @app.post(WEBHOOK_PATH)
# async def webhook_endpoint(request: Request):
#     try:
#         # So‘rovni Telegram Update obyektiga aylantirish
#         update = types.Update(**await request.json())
#         # Dispatcher yordamida webhook update-ni qayta ishlash
#         await dp.feed_webhook_update(bot, update)
#         return JSONResponse(content={"status": "success"})
#     except Exception as e:
#         logging.error(f"Webhook processing error: {e}")
#         raise HTTPException(status_code=500, detail="Internal Server Error")


async def start_polling():
    logger.info("Starting polling")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    import uvicorn
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "polling":
        asyncio.run(start_polling())
    else:
        uvicorn.run(app, host=WEBAPP_HOST, port=WEBAPP_PORT)
