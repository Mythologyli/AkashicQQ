import json

from nonebot import on_command
from nonebot import logger
from nonebot.adapters.cqhttp import Bot, Message, MessageEvent


welcome_msg: str = json.loads(
    open('./config/text.json', 'r').read())['welcome']['message']

cmd_set: dict = json.loads(open('./config/cmd_alias.json', 'r').read())['welcome']
welcome = on_command(cmd_set['cmd'], aliases=set(cmd_set['aliases']))


@welcome.handle()
async def handle_welcome(bot: Bot, event: MessageEvent):
    arg = str(event.message).strip()

    if not arg:  # 用户未发送参数
        at_msg = ''

    else:  # 用户发送参数
        at_msg = Message(arg + '\n')

    logger.info('发送欢迎消息')
    logger.debug(f"欢迎消息：{welcome_msg}")

    await welcome.send(at_msg + welcome_msg)
