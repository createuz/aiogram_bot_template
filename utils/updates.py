import secrets
from typing import Any

import aiohttp.web
import aiojobs
from aiogram import Bot, Dispatcher, types
from aiohttp import web

from data.config import conf

tg_updates_app = web.Application()


async def process_update(upd: types.Update, bot: Bot, dp: Dispatcher, workflow_data: dict[str, Any]) -> None:
    await dp.feed_webhook_update(bot, upd, **workflow_data)


async def execute(req: web.Request) -> web.Response:
    if not secrets.compare_digest(
            req.headers.get("X-Telegram-Bot-Api-Secret-Token", ""),
            conf.webhook.secret_token,
    ):
        raise aiohttp.web.HTTPNotFound()
    dp: Dispatcher = req.app["dp"]
    if not secrets.compare_digest(req.match_info["token"], conf.bot_token.token):
        raise aiohttp.web.HTTPNotFound()
    scheduler: aiojobs.Scheduler = req.app["scheduler"]
    if scheduler.pending_count >= conf.webhook.max_updates_in_queue:
        raise web.HTTPTooManyRequests()
    if scheduler.closed:
        raise web.HTTPServiceUnavailable(reason="Closed queue")
    await scheduler.spawn(
        process_update(
            types.Update(**(await req.json())),
            req.app["bot"],
            dp,
            {"dp": dp}
        )
    )
    return web.Response()


tg_updates_app.add_routes([web.post("/bot/{token}", execute)])
