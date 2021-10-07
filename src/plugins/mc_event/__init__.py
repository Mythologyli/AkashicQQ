import json
import asyncio

import nonebot
from nonebot.log import logger
from nonebot.adapters.cqhttp import Bot
from fastapi import Body, FastAPI

import prism_api


config: dict = json.loads(open('./config/mc_event.json', 'r').read())
group_config: dict = json.loads(open('./config/group.json', 'r').read())
text: dict = json.loads(open('./config/text.json', 'r').read())['mc_event']
not_bind_msg_in_game: str = json.loads(
    open('./config/text.json', 'r').read())['bind_qq']['not_bind_msg_in_game']


app: FastAPI = nonebot.get_app()


@app.post('/')
async def mc_event_handler(data: dict = Body(...)):
    data = data['data']
    logger.info(f"收到MC事件: {data}")

    while True:
        try:
            bot: Bot = nonebot.get_bot()
        except ValueError:
            asyncio.sleep(0)
        else:
            break

    # 处理事件
    if data['type'] == 'ServerStart':
        await server_start_handler(bot, data)
    elif data['type'] == 'ServerStop':
        await server_stop_handler(bot, data)
    elif data['type'] == 'PlayerJoin':
        await player_join_handler(bot, data)
    elif data['type'] == 'PlayerAdvancement':
        await player_advancement_handler(bot, data)
    elif data['type'] == 'PlayerChat':
        await player_chat_handler(bot, data)
    elif data['type'] == 'PlayerQuit':
        await player_quit_handler(bot, data)

    return {
        "status": 200,
        "msg": "success"
    }


async def server_start_handler(bot: Bot, data: dict):
    if config['enable']['server_start'] == False:
        return

    message = text['server_start'].replace('<tag>', data['tag']).replace(
        '<time>', str(data['start_use_time']))

    await bot.send_group_msg(group_id=group_config['main_group'], message=message)


async def server_stop_handler(bot: Bot, data: dict):
    if config['enable']['server_stop'] == False:
        return

    message = text['server_stop'].replace('<tag>', data['tag'])

    await bot.send_group_msg(group_id=group_config['main_group'], message=message)


async def player_join_handler(bot: Bot, data: dict):
    if config['enable']['player_join'] == False:
        return

    message = text['player_join'].replace(
        '<player>', data['player']).replace('<tag>', data['tag'])

    await bot.send_group_msg(group_id=group_config['main_group'], message=message)

    prism_data = {
        'message': f"§5[{data['tag']}] §f" + message,
        'selector': '@a'
    }

    # 向其他服务器广播消息
    for server in prism_api.config['server']:
        if data['tag'] != server['tag']:
            await prism_api.post(api='/tellraw', data=prism_data, server_tag=server['tag'])

    # 检测玩家是否绑定账号
    try:
        record = json.loads(open('./data/bind_qq.json', 'r').read())
        players = list(record.values())
    except FileNotFoundError:
        players = []

    # 玩家未绑定账号
    if data['player'] not in players:
        prism_data = {
            'message': not_bind_msg_in_game.replace('<player>', data['player']),
            'selector': data['player']
        }

        await prism_api.post(api='/tellraw', data=prism_data, server_tag=data['tag'])
        logger.info(f"加入服务器{data['tag']}的玩家{data['player']}未绑定账号，已向其发送提示")


async def player_advancement_handler(bot: Bot, data: dict):
    if config['enable']['player_advancement'] == False:
        return

    # 检查成就翻译
    try:
        tranlation = json.loads(
            open('./data/advancement_translation.json', 'r').read())
    except FileNotFoundError:
        tranlation = {}

    for adv in tranlation:
        if adv['en'].lower().strip() == data['advancement'].lower().strip():
            data['advancement'] = adv['zh_cn']
            break

    message = text['player_advancement'].replace(
        '<player>', data['player']).replace('<advancement>', data['advancement']).replace('<tag>', data['tag'])

    await bot.send_group_msg(group_id=group_config['main_group'], message=message)

    prism_data = {
        'message': f"§5[{data['tag']}] §f" + message,
        'selector': '@a'
    }

    # 向其他服务器广播消息
    for server in prism_api.config['server']:
        if data['tag'] != server['tag']:
            await prism_api.post(api='/tellraw', data=prism_data, server_tag=server['tag'])


async def player_chat_handler(bot: Bot, data: dict):
    if config['enable']['player_chat'] == False:
        return

    message = text['player_chat'].replace(
        '<player>', data['player']).replace('<message>', data['message']).replace('<tag>', data['tag'])

    await bot.send_group_msg(group_id=group_config['main_group'], message=message)

    prism_data = {
        'message': f"§5[{data['tag']}] §f" + message,
        'selector': '@a'
    }

    # 向其他服务器广播消息
    for server in prism_api.config['server']:
        if data['tag'] != server['tag']:
            await prism_api.post(api='/tellraw', data=prism_data, server_tag=server['tag'])


async def player_quit_handler(bot: Bot, data: dict):
    if config['enable']['player_quit'] == True:
        message = text['player_quit'].replace(
            '<player>', data['player']).replace('<tag>', data['tag'])

        await bot.send_group_msg(group_id=group_config['main_group'], message=message)

        prism_data = {
            'message': f"§5[{data['tag']}] §f" + message,
            'selector': '@a'
        }

        # 向其他服务器广播消息
        for server in prism_api.config['server']:
            if data['tag'] != server['tag']:
                await prism_api.post(api='/tellraw', data=prism_data, server_tag=server['tag'])

    if config['enable']['player_quit_private'] == True:
        # 向本人发送消息，提醒下线
        try:
            record = json.loads(open('./data/bind_qq.json', 'r').read())
        except FileNotFoundError:
            record = {}

        for key in record:
            if record[key] == data['player']:
                message = text['player_quit_private'].replace(
                    '<player>', data['player']).replace('<tag>', data['tag'])

                await bot.send_private_msg(user_id=int(key), message=message)
