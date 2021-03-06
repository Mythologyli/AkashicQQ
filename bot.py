#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import nonebot
from nonebot import logger
from nonebot.adapters.cqhttp import Bot as CQHTTPBot


# dev 环境下监控 src config 文件夹变动
nonebot.init(fastapi_reload_dirs=['src', 'config'])

logger.add("./logs/{time:YYYY-MM-DD}.log", rotation="0:00")

app = nonebot.get_asgi()

driver = nonebot.get_driver()
driver.register_adapter("cqhttp", CQHTTPBot)

nonebot.load_from_toml("pyproject.toml")
