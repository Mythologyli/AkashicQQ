import json
import asyncio

import nonebot
from nonebot.log import logger
from nonebot import require
from nonebot.adapters.cqhttp import Bot, MessageSegment
import httpx


config = json.loads(open('./config/bilibililive_checker.json', 'r').read())
text: str = json.loads(
    open('./config/text.json', 'r').read())['bilibililive_checker']['message']

live_status = [False for i in range(len(config['liveroom']))]

scheduler = require("nonebot_plugin_apscheduler").scheduler


@scheduler.scheduled_job("cron", second="*/5")
async def bilibili_checker_handler():
    if config['enable'] == False:
        return

    post_data = {
        'uids': config['liveroom']
    }

    async with httpx.AsyncClient() as client:
        res = await client.post(url='https://api.live.bilibili.com/room/v1/Room/get_status_info_by_uids', json=post_data)
        res = res.json()

        if res['code'] != 0:
            return

        for i in range(len(config['liveroom'])):
            if res['data'][str(config['liveroom'][i])]['live_status'] == 1:
                logger.debug(f"uid为{config['liveroom'][i]}的主播正在直播！")

                if live_status[i] == False:

                    live_status[i] = True

                    at_msg = MessageSegment.at('all') + ''

                    msg = text.replace('<name>', res['data'][str(config['liveroom'][i])]['uname']).replace(
                        '<title>', res['data'][str(config['liveroom'][i])]['title']).replace(
                        '<area>', res['data'][str(config['liveroom'][i])]['area_v2_name']).replace(
                        '<url>', f"https://live.bilibili.com/{res['data'][str(config['liveroom'][i])]['room_id']}") + \
                        MessageSegment.image(
                            res['data'][str(config['liveroom'][i])]['cover_from_user'])

                    # 获取机器人
                    while True:
                        try:
                            bot: Bot = nonebot.get_bot()
                        except ValueError:
                            asyncio.sleep(0)
                        else:
                            break

                    for group_id in config['group']:
                        # 单独发送 @全体成员，防止次数耗尽导致完全收不到消息
                        await bot.send_group_msg(group_id=group_id, message=at_msg)
                        await bot.send_group_msg(group_id=group_id, message=msg)

                    logger.info(
                        f"uid为{config['liveroom'][i]}的主播正在直播，发送消息到群{config['group']}")

            else:
                logger.debug(f"uid为{config['liveroom'][i]}的主播未在直播！")

                if live_status[i] == True:
                    live_status[i] = False
