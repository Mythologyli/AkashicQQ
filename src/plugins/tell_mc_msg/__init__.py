import json

from nonebot import on_command
from nonebot import logger
from nonebot.adapters.cqhttp import Bot, MessageSegment, MessageEvent

import prism_api


not_bind_when_send_msg: str = json.loads(
    open('./config/text.json', 'r').read())['bind_qq']['not_bind_when_send_msg']
text: dict = json.loads(open('./config/text.json', 'r').read())['tell_mc_msg']

cmd_set: dict = json.loads(open('./config/cmd_alias.json', 'r').read())['tell_mc_msg']
tell_mc_msg = on_command(cmd_set['cmd'], aliases=set(cmd_set['aliases']))


@tell_mc_msg.handle()
async def handle_tell_mc_msg(bot: Bot, event: MessageEvent):
    # 发送者 user_card
    user_id = event.user_id
    at_msg = MessageSegment.at(user_id) + '\n'

    # 检查发送者是否绑定账号
    record = json.loads(open('./data/bind_qq.json', 'r').read())

    if str(user_id) not in record:
        logger.info(f"{user_id}试图向服务器私聊消息但未绑定账号，已拒绝")
        await tell_mc_msg.send(at_msg + not_bind_when_send_msg)
        return

    user_card = record[str(user_id)]

    # 发送消息
    stripped_arg = str(event.message).strip()

    index = stripped_arg.find(' ')
    player_id = stripped_arg[0:index]
    msg_to_send = (stripped_arg[index + 1:len(stripped_arg)])

    if player_id == '' or msg_to_send == '' or index == -1:
        logger.info(f"{user_id}发送格式错误！私聊消息请求被拒绝")
        await tell_mc_msg.send(at_msg + text['format_error'])
        return

    data = {
        'message': text['msg_in_game'].replace('<bind_player>', user_card).replace('<msg>', msg_to_send),
        'selector': player_id
    }

    await prism_api.all_server_tellraw(data=data)
    logger.info(f"{user_id}向{player_id}私聊消息：{msg_to_send}")
