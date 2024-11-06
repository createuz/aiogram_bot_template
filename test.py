from aiogram import Router, F, Bot, types
from aiogram.filters import Command
from aiogram.types import Message, PreCheckoutQuery
from aiogram import Dispatcher
import asyncio

import logging

from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)

dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

router = Router()


@dp.message(Command('start'))
async def create_invoice(msg: Message):
    Upscale = types.LabeledPrice(label='birinchi oy', amount=1250)

    await bot.send_invoice(
        msg.chat.id,
        title="One little buy",
        description="One little buy",
        provider_token="",
        currency="XTR",
        photo_url="https://media.dev.to/cdn-cgi/image/width=800%2Cheight=%2Cfit=scale-down%2Cgravity=auto%2Cformat=auto/https%3A%2F%2Fdev-to-uploads.s3.amazonaws.com%2Fuploads%2Farticles%2F2amqwz8zpf6cahrtf6c8.png",
        photo_width=3600,
        photo_height=2338,
        photo_size=262000,
        is_flexible=False,
        prices=[Upscale],
        start_parameter="one-upscale",
        payload="one-upscale"
    )


@router.pre_checkout_query()
async def checkout_handler(checkout_query: PreCheckoutQuery):
    await checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def star_payment(msg: Message, bot: Bot):
    await bot.refund_star_payment(
        msg.chat.id,
        msg.successful_payment.telegram_payment_charge_id,
    )

    await msg.answer(f"Your transaction id: {msg.successful_payment.telegram_payment_charge_id}")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
