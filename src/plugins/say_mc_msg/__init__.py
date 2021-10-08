import json

from nonebot import on_command
from nonebot import logger
from nonebot.adapters.cqhttp import Bot, MessageSegment, MessageEvent

import prism_api


not_bind_when_send_msg: str = json.loads(
    open('./config/text.json', 'r', encoding='utf-8').read())['bind_qq']['not_bind_when_send_msg']
text: dict = json.loads(open('./config/text.json', 'r', encoding='utf-8').read())['say_mc_msg']

cmd_set: dict = json.loads(open('./config/cmd_alias.json', 'r', encoding='utf-8').read())['say_mc_msg']
say_mc_msg = on_command(cmd_set['cmd'], aliases=set(cmd_set['aliases']))


@say_mc_msg.handle()
async def handle_say_mc_msg(bot: Bot, event: MessageEvent):
    # 发送者 user_id
    user_id = event.user_id
    at_msg = MessageSegment.at(user_id) + '\n'

    # 检查发送者是否绑定账号
    try:
        record = json.loads(open('./data/bind_qq.json', 'r', encoding='utf-8').read())
    except FileNotFoundError:
        record = {}

    if str(user_id) not in record:
        logger.info(f"{user_id}试图向服务器发送消息但未绑定账号，已拒绝")
        await say_mc_msg.send(at_msg + not_bind_when_send_msg)
        return

    user_card = record[str(user_id)]

    # 发送消息
    msg_to_send = str(event.message).strip()

    if msg_to_send == '':
        logger.info(f"{user_id}发送格式错误！发送消息请求被拒绝")
        await say_mc_msg.send(at_msg + text['format_error'])
        return

    data = {
        'message': text['msg_in_game'].replace('<bind_player>', user_card).replace('<msg>', msg_to_send),
        'selector': '@a'
    }

    await prism_api.all_server_tellraw(data=data)
    logger.info(f"{user_id}向服务器发送消息：{msg_to_send}")
