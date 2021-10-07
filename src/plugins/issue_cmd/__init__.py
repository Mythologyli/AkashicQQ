import json

from nonebot import on_command
from nonebot.log import logger
from nonebot.adapters.cqhttp import Bot, MessageSegment, MessageEvent

import prism_api


op_user: list = json.loads(open('./config/group.json', 'r').read())['op_user']
text: dict = json.loads(open('./config/text.json', 'r').read())['issue_cmd']

cmd_set: dict = json.loads(
    open('./config/cmd_alias.json', 'r').read())['issue_cmd']
issue_cmd = on_command(cmd_set['cmd'], aliases=set(cmd_set['aliases']))


@issue_cmd.handle()
async def handle_issue_cmd(bot: Bot, event: MessageEvent):
    # 发送者 user_id
    user_id = event.user_id
    at_msg = MessageSegment.at(user_id) + '\n'

    string = str(event.message).strip()
    arg_list = string.split(',')

    logger.info(f"{user_id}试图执行命令：{arg_list}")

    # 鉴权
    if user_id not in op_user:
        await issue_cmd.send(at_msg + text['no_permission'])
        logger.debug(f"op_user为：{op_user}")
        logger.info(f"{user_id}试图执行命令但无权限")
        return

    # 处理命令格式，参数分别为 cmd num wait_time server_tag
    cmd = arg_list[0]

    if cmd == '':
        await issue_cmd.send(at_msg + text['format_error'])
        logger.info(f"{user_id}发送格式错误！执行命令请求被拒绝")
        return

    if len(arg_list) > 1:
        num = int(arg_list[1])
    else:
        num = 1

    if len(arg_list) > 2:
        wait_time = int(arg_list[2])
    else:
        wait_time = 1

    if len(arg_list) > 3:
        server = arg_list[3]

        exist_server_tag_list = []
        for server in prism_api.config['server']:
            exist_server_tag_list.append(server['tag'])

        if server not in exist_server_tag_list:
            await issue_cmd.send(at_msg + text['server_tag_not_exist'])
            logger.info("服务器不存在！执行命令请求被拒绝")
            return

    else:
        server = None

    # 发送命令
    res = await prism_api.server_cmd(cmd=cmd, num=num, wait_time=wait_time, server_tag=server)

    # 回传结果
    msg = text['answer'].replace('<res>', res)
    await issue_cmd.send(at_msg + msg)
    logger.info(f"命令执行结果：{res}")
