import json

from nonebot import on_notice
from nonebot.log import logger
from nonebot.adapters.cqhttp import Bot, MessageSegment, GroupIncreaseNoticeEvent

import utils


welcome_msg: str = json.loads(
    open('./config/text.json', 'r').read())['welcome']['message']

group_increase = on_notice()


@group_increase.handle()
async def handle_group_increase(bot: Bot, event: GroupIncreaseNoticeEvent):
    # 入群者 user_id
    user_id = event.user_id
    at_msg = MessageSegment.at(user_id) + '\n'

    # 发送入群欢迎消息
    await group_increase.send(at_msg + welcome_msg)
    logger.info(f"向{user_id}发送入群欢迎消息")
    logger.debug(f"欢迎消息：{welcome_msg}")

    # 向管理员提示新增成员
    user_id = event.user_id
    group_id = event.group_id
    await utils.inform_admin(message='进入群' + str(group_id), member_user_id=user_id)
