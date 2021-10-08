import json

from nonebot import on_command
from nonebot import logger
from nonebot.adapters.cqhttp import Bot, MessageSegment, MessageEvent

import prism_api


text: dict = json.loads(open('./config/text.json', 'r', encoding='utf-8').read())['query_online']

cmd_set: dict = json.loads(open('./config/cmd_alias.json', 'r', encoding='utf-8').read())['query_online']
query_online = on_command(cmd_set['cmd'], aliases=set(cmd_set['aliases']))


@query_online.handle()
async def handle_query_online(bot: Bot, event: MessageEvent):
    for server in prism_api.config['server']:
        res = await prism_api.get(api='/list', server_tag=server['tag'])
        tag = res['data']['tag']
        res = res['data']['player_list']

        num = len(res)
        if num == 0:
            msg = text['no_player'].replace('<tag>', tag)
        else:
            player_list = ''
            for i in range(num):
                if i == 0:
                    player_list += res[i]
                else:
                    player_list += ', ' + res[i]
            msg = text['list_player'].replace(
                '<num>', str(num)).replace('<list>', player_list).replace('<tag>', tag)

        logger.info(f"查询在线人数：{tag} {res}")
        await query_online.send(msg)
