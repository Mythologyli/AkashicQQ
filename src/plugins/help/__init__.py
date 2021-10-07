import json
from typing import Dict

from nonebot import on_command
from nonebot import logger
from nonebot.adapters.cqhttp import Bot, Message, MessageEvent


text: dict = json.loads(open('./config/text.json', 'r').read())

cmd_set: dict = json.loads(open('./config/cmd_alias.json', 'r').read())['help']
help = on_command(cmd_set['cmd'], aliases=set(cmd_set['aliases']))


@help.handle()
async def handle_help(bot: Bot, event: MessageEvent):
    logger.info('请求帮助')

    msg = ''

    for key in text:
        if type(text[key]) == type({}):
            if 'help' in text[key]:
                msg += text[key]['help'] + '\n'

    await help.send(msg)
