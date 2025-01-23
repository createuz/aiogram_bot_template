import asyncio
from typing import Tuple

import aiojobs
from aiogram import Bot, Dispatcher
from aiogram import Router
from aiohttp import web

from data import setup_logger, conf
from data.middleware import StructLoggingMiddleware
from db.postgres import create_db_connections, close_db_connections
from handlers import user_router, anon_msg_router, statistic_router, ads_router, panel_router
from utils.updates import tg_updates_app


def register_routers(dp: Dispatcher, routers: Tuple[Router, ...]) -> None:
    for router in routers:
        dp.include_router(router)


def setup_handlers(dp: Dispatcher) -> None:
    routers = (user_router, anon_msg_router, statistic_router, ads_router, panel_router)
    register_routers(dp, routers)


def setup_middlewares(dp: Dispatcher) -> None:
    dp.update.outer_middleware(StructLoggingMiddleware(logger=dp["aiogram_logger"]))


def setup_logging(dp: Dispatcher) -> None:
    dp["aiogram_logger"] = setup_logger().bind(type="aiogram")
    dp["db_logger"] = setup_logger().bind(type="db")
    dp["cache_logger"] = setup_logger().bind(type="cache")
    dp["business_logger"] = setup_logger().bind(type="business")


async def setup_aiogram(dp: Dispatcher) -> None:
    setup_logging(dp)
    logger = dp["aiogram_logger"]
    logger.debug("Configuring aiogram")
    await create_db_connections(dp)
    setup_handlers(dp)
    setup_middlewares(dp)
    logger.info("Configured aiogram")


async def aiohttp_on_startup(app: web.Application) -> None:
    dp: Dispatcher = app["dp"]
    workflow_data = {"app": app, "dispatcher": dp}
    if "bot" in app:
        workflow_data["bot"] = app["bot"]
    await dp.emit_startup(**workflow_data)


async def aiohttp_on_shutdown(app: web.Application) -> None:
    dp: Dispatcher = app["dp"]
    for i in [app, *app._subapps]:  # dirty
        if "scheduler" in i:
            scheduler: aiojobs.Scheduler = i["scheduler"]
            scheduler._closed = True
            while scheduler.pending_count != 0:
                dp["aiogram_logger"].info(
                    f"Waiting for {scheduler.pending_count} tasks to complete"
                )
                await asyncio.sleep(1)
    workflow_data = {"app": app, "dispatcher": dp}
    if "bot" in app:
        workflow_data["bot"] = app["bot"]
    await dp.emit_shutdown(**workflow_data)


async def aiogram_on_startup_webhook(dispatcher: Dispatcher, bot: Bot) -> None:
    await setup_aiogram(dispatcher)
    webhook_logger = dispatcher["aiogram_logger"].bind(webhook_url=conf.webhook.url)
    webhook_logger.debug("Configuring webhook")
    webhook_url = f"{conf.webhook.url}/webhook/{conf.bot_token.token}"
    webhook_path = f"/webhook/{conf.bot_token.token}"
    await bot.set_webhook(
        url=webhook_url,
        allowed_updates=dispatcher.resolve_used_update_types(),
        secret_token=conf.webhook.secret_token,
    )
    webhook_logger.info("Configured webhook")


async def aiogram_on_shutdown_webhook(dispatcher: Dispatcher, bot: Bot) -> None:
    dispatcher["aiogram_logger"].debug("Stopping webhook")
    await close_db_connections(dispatcher)
    await bot.session.close()
    await dispatcher.storage.close()
    dispatcher["aiogram_logger"].info("Stopped webhook")


async def aiogram_on_startup_polling(dispatcher: Dispatcher, bot: Bot) -> None:
    await bot.delete_webhook(drop_pending_updates=False)
    await setup_aiogram(dispatcher)
    dispatcher["aiogram_logger"].info("Started polling")


async def aiogram_on_shutdown_polling(dispatcher: Dispatcher, bot: Bot) -> None:
    dispatcher["aiogram_logger"].debug("Stopping polling")
    await close_db_connections(dispatcher)
    await bot.session.close()
    await dispatcher.storage.close()
    dispatcher["aiogram_logger"].info("Stopped polling")


async def setup_aiohttp_app(bot: Bot, dp: Dispatcher) -> web.Application:
    scheduler = aiojobs.Scheduler()
    app = web.Application()
    subapps: list[tuple[str, web.Application]] = [("/bot/webhook/", tg_updates_app)]
    for prefix, subapp in subapps:
        subapp["bot"] = bot
        subapp["dp"] = dp
        subapp["scheduler"] = scheduler
        app.add_subapp(prefix, subapp)
    app["bot"] = bot
    app["dp"] = dp
    app["scheduler"] = scheduler
    app.on_startup.append(aiohttp_on_startup)
    app.on_shutdown.append(aiohttp_on_shutdown)
    return app
