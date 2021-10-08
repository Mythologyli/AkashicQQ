import json

from nonebot import on_command
from nonebot.log import logger
from nonebot.adapters.cqhttp import Bot, MessageSegment, MessageEvent

import utils
import prism_api


text: dict = json.loads(open('./config/text.json', 'r', encoding='utf-8').read())['bind_qq']

cmd_set: dict = json.loads(open('./config/cmd_alias.json', 'r', encoding='utf-8').read())['bind_qq']
bind_qq = on_command(cmd_set['cmd'], aliases=set(cmd_set['aliases']))


@bind_qq.handle()
async def handle_bind_qq(bot: Bot, event: MessageEvent):
    # 发送者 user_id
    user_id = event.user_id
    at_msg = MessageSegment.at(user_id) + '\n'

    # 发送者要绑定的玩家
    player_to_bind = str(event.message).strip()

    # 检测格式
    if player_to_bind == '':
        await bind_qq.send(at_msg + text['format_error'])
        logger.info(f"{user_id}发送格式错误！绑定请求被拒绝")
        return

    logger.info(f"{user_id}尝试绑定{player_to_bind}")

    # 检测是否绑定过
    try:
        record = json.loads(open('./data/bind_qq.json', 'r', encoding='utf-8').read())
    except FileNotFoundError:
        record = {}

    if str(user_id) in record:
        await bind_qq.send(at_msg + text['already_bind'])
        logger.debug(f"bind_qq表：{record}")
        logger.info(f"{user_id}已绑定过！绑定请求被拒绝")
        return

    # 获取所有登录过的玩家列表，用于检测 ID 是否真实存在
    res = []

    # 获取所有服务器的 usercache 表
    for server in prism_api.config['server']:
        prism_res = await prism_api.get(api='/usercache', server_tag=server['tag'])
        res += prism_res['data']['usercache']

    players = []

    for player in res:
        players.append(player['name'])

    # ID 不存在
    if player_to_bind not in players:
        await bind_qq.send(at_msg + text['player_not_exist'])
        logger.debug(f"usercache表：{res}")
        logger.info(f"{user_id}要绑定的玩家不存在！绑定请求被拒绝")
        return

    record[str(user_id)] = player_to_bind

    with open('./data/bind_qq.json', 'w') as fp:
        fp.write(json.dumps(record))
        fp.close()

    await bind_qq.send(at_msg + text['success'])

    # 通知管理员
    await utils.inform_admin(message='绑定了游戏账号：' + player_to_bind, member_user_id=user_id)
