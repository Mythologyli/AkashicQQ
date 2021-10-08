import json

from nonebot import on_command
from nonebot.log import logger
from nonebot.adapters.cqhttp import Bot, MessageSegment, MessageEvent

import utils
import prism_api


not_bind_when_send_msg: str = json.loads(
    open('./config/text.json', 'r', encoding='utf-8').read())['bind_qq']['not_bind_when_send_msg']
text: dict = json.loads(open('./config/text.json', 'r', encoding='utf-8').read())['call_admin']

cmd_set: dict = json.loads(open('./config/cmd_alias.json', 'r', encoding='utf-8').read())['call_admin']
call_admin = on_command(cmd_set['cmd'], aliases=set(cmd_set['aliases']))


@call_admin.handle()
async def handle_call_admin(bot: Bot, event: MessageEvent):
    # 发送者 user_id
    user_id = event.user_id
    at_msg = MessageSegment.at(user_id) + '\n'

    # 内容
    msg_to_send = str(event.message).strip()

    # 检测格式
    if msg_to_send == '':
        await call_admin.send(at_msg + text['format_error'])
        logger.info(f"{user_id}发送格式错误！呼叫管理员请求被拒绝")
        return

    logger.info(f"{user_id}尝试呼叫管理员：{msg_to_send}")

    # 检查发送者是否绑定账号
    try:
        record = json.loads(open('./data/bind_qq.json', 'r', encoding='utf-8').read())
    except FileNotFoundError:
        record = {}

    if str(user_id) not in record:
        logger.info(f"{user_id}试图向管理员发送消息但未绑定账号，已拒绝")
        await call_admin.send(at_msg + not_bind_when_send_msg)
        return

    # 在 QQ 中通知管理员
    await utils.inform_admin(message='向管理员发送消息：' + msg_to_send, member_user_id=user_id)

    # 获取群昵称
    res = await bot.get_group_member_info(group_id=utils.config['main_group'], user_id=user_id)

    if 'card' not in res:
        user_card = res['nickname']
    else:
        user_card = res['card']

    # 尝试在游戏内通知管理员
    for admin_user_id in utils.config['admin_user']:
        if str(admin_user_id) in record:
            prism_data = {
                'message': f"§5[QQ] §f{user_card} 向管理员发送消息：" + msg_to_send,
                'selector': record[str(admin_user_id)]
            }

            await prism_api.all_server_tellraw(data=prism_data)
