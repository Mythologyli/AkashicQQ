import json

from nonebot import on_command
from nonebot.typing import T_State
from nonebot import logger
from nonebot.adapters.cqhttp import Bot, MessageSegment, MessageEvent

import utils
import prism_api


config: list = json.loads(open('./config/cmd_register.json', 'r').read())
text: dict = json.loads(open('./config/text.json', 'r').read())['cmd_register']

cmd_list: list = [one_cmd['cmd'] for one_cmd in config]

for one_cmd in config:
    cmd_list += one_cmd['aliases']

cmd_register = on_command('cmd_register', aliases=set(cmd_list))


@cmd_register.handle()
async def handle_cmd_register(bot: Bot, event: MessageEvent, state: T_State):
    # 发送者 user_card
    user_id = event.user_id
    at_msg = MessageSegment.at(user_id) + '\n'

    for cmd in config:
        cmd_and_aliases = [cmd['cmd']]
        cmd_and_aliases += cmd['aliases']

        # 匹配到命令
        if state['_prefix']['command'][0] in cmd_and_aliases:
            logger.info(f"{user_id}试图执行命令：{cmd['cmd']}")

            # 开始鉴权
            if cmd['permission'] == 'ALL' or \
                    user_id in utils.config['op_user'] or \
                    (cmd['permission'] == 'ADMIN' and user_id in utils.config['admin_user']) or \
                    user_id in cmd['allow_member']:
                arg = str(event.message).strip()

                if arg != '' and cmd['no_arg']:
                    logger.info(f"{user_id}试图为不可添加参数的命令添加参数")
                    await cmd_register.send(at_msg + text['extra_arg'])
                    return

                real_cmd = cmd['cmd'] + ' ' + arg

                res = await prism_api.server_cmd(cmd=real_cmd, num=cmd['num'], wait_time=cmd['wait_time'], server_tag=cmd['server_tag'])
                msg = text['answer'].replace('<res>', res)
                await cmd_register.send(at_msg + msg)
                logger.info(f"命令执行结果：{res}")
            else:
                logger.info(f"{user_id}试图执行命令但无权限")
                await cmd_register.send(at_msg + text['no_permission'])
