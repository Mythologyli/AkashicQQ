import json
import asyncio

import nonebot
from nonebot import logger
from nonebot.adapters.cqhttp import Bot


config = json.loads(open('./config/group.json', 'r').read())


async def inform_admin(message: str, member_user_id: int = None):
    while True:
        try:
            bot: Bot = nonebot.get_bot()
        except ValueError:
            asyncio.sleep(0)
        else:
            break

    # 指定 member_user_id
    if member_user_id != None:
        # 获取 member 群昵称
        res = await bot.get_group_member_info(group_id=config['main_group'], user_id=member_user_id)

        if 'card' not in res:
            user_card = res['nickname']
        else:
            user_card = res['card']

        for i in range(len(config['admin_user'])):
            await bot.send_private_msg(user_id=config['admin_user'][i], message=f"{user_card}({member_user_id}){message}")

        logger.info(f"{user_card}({member_user_id}){message}")

    else:
        for i in range(len(config['admin_user'])):
            await bot.send_private_msg(user_id=config['admin_user'][i], message=message)

        logger.info(message)
