# import logging
# import sys
# from typing import Tuple
#
# from aiogram import Bot, Dispatcher, Router
# from aiogram.fsm.storage.memory import MemoryStorage
# from aiogram.types import BotCommand
#
# from handlers.admins import ads_router, panel_router
#
# API_TOKEN = "7189528230:AAEayeWCvI0Jv7YufsMLW8CmqcLPQObbxyg"
#
#
# def register_routers(dp: Dispatcher, routers: Tuple[Router, ...]) -> None:
#     for router in routers:
#         dp.include_router(router)
#
#
# async def main():
#     bot = Bot(token=API_TOKEN)
#     dp = Dispatcher(storage=MemoryStorage())
#     routers = (ads_router, panel_router)
#     register_routers(dp=dp, routers=routers)
#     await bot.set_my_commands([BotCommand(command="/ads", description="Create an ad")])
#     await dp.start_polling(bot)
#
#
# if __name__ == "__main__":
#     import asyncio
#
#     logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
#     asyncio.run(main())
