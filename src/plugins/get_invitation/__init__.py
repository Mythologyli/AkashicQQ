import time
import string
import random
import json

from nonebot import on_command
from nonebot import logger
from nonebot.adapters.cqhttp import Bot, MessageSegment, MessageEvent
import aiomysql

import utils


config: dict = json.loads(open('./config/get_invitation.json', 'r', encoding='utf-8').read())
text: dict = json.loads(
    open('./config/text.json', 'r', encoding='utf-8').read())['get_invitation']

cmd_set: dict = json.loads(open('./config/cmd_alias.json', 'r', encoding='utf-8').read())['get_invitation']
get_invitation = on_command(cmd_set['cmd'], aliases=set(cmd_set['aliases']))


@get_invitation.handle()
async def handle_get_invitation(bot: Bot, event: MessageEvent):
    # 发送者 user_id
    user_id = event.user_id
    at_msg = MessageSegment.at(user_id) + '\n'

    # 鉴定发起者是否有剩余次数
    try:
        record = json.loads(open('./data/invitation.json', 'r', encoding='utf-8').read())
    except FileNotFoundError:
        record = {}

    # 不存在记录，设置为初始值
    if str(user_id) not in record:
        if user_id not in utils.config['admin_user']:
            record[str(user_id)] = config['initial_chance']
        else:
            record[str(user_id)] = 1

    # 有剩余机会或请求者为管理员，则为其生成邀请码
    if record[str(user_id)] > 0 or user_id in utils.config['admin_user']:
        conn = await aiomysql.connect(
            host=config['blessing_skin_server_mysql']['host'],
            port=config['blessing_skin_server_mysql']['port'],
            user=config['blessing_skin_server_mysql']['user'],
            password=config['blessing_skin_server_mysql']['password'],
            db=config['blessing_skin_server_mysql']['db']
        )

        cur = await conn.cursor()
        await cur.execute("SELECT id FROM invitation_codes")
        res = await cur.fetchall()

        new_id = max(res)[0] + 1
        code = f"from{user_id}_" + \
            ''.join(random.sample(string.ascii_letters + string.digits, 8))
        time_stamp = time.strftime(
            '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

        await cur.execute(
            "INSERT INTO `invitation_codes` (`id`, `code`, `generated_at`, `used_by`, `used_at`) " +
            f"VALUES ('{new_id}', '{code}', '{time_stamp}', '0', NULL)"
        )
        await conn.commit()
        conn.close()

        msg = text['get_msg'].replace('<code>', code)
        await get_invitation.send(at_msg + msg)

        # 非管理员，次数减一
        if user_id not in utils.config['admin_user']:
            record[str(user_id)] -= 1

        with open('./data/invitation.json', 'w') as fp:
            fp.write(json.dumps(record))
            fp.close()

        # 通知管理员
        await utils.inform_admin(message='索取了邀请码：' + code, member_user_id=user_id)

    else:
        msg = text['no_chance']
        await get_invitation.send(at_msg + msg)

        # 通知管理员
        await utils.inform_admin(message='试图索取邀请码，但邀请次数已耗尽', member_user_id=user_id)
