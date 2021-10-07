import json
import re

from nonebot.log import logger
import httpx


config = json.loads(open('./config/mc_server.json', 'r').read())


async def get(api: str, server_tag: str = None):
    if server_tag == None:
        server_tag = config['main_server_tag']

    for server in config['server']:
        if server['tag'] == server_tag:
            url = server['url']

    async with httpx.AsyncClient() as client:
        logger.debug(f"发送prism_api.get：{url + api} server={server_tag}")
        resp = await client.get(url=url + api, timeout=10)
        resp = resp.json()
        logger.debug(f"prism_api.get回复：{resp}")
        return resp


async def post(api: str, data: dict = [], server_tag: str = None):
    if server_tag == None:
        server_tag = config['main_server_tag']

    for server in config['server']:
        if server['tag'] == server_tag:
            url = server['url']

    async with httpx.AsyncClient() as client:
        logger.debug(
            f"发送prism_api.post：{url + api} data={data} server={server_tag}")
        resp = await client.post(url=url + api, json=data, timeout=10)
        resp = resp.json()
        logger.debug(f"prism_api.post回复：{resp}")
        return resp


async def server_cmd(cmd: str, num: int = 1, wait_time: int = 1, server_tag: str = None):
    data = {
        'cmd': cmd,
        'num': num,
        'wait_time': wait_time
    }

    logger.debug(f"发送prism_api.server_cmd：data={data} server={server_tag}")
    res = await post(api='/cmd', data=data, server_tag=server_tag)

    if res['status'] == 200:
        res_str = ''
        for string in res['data']['list']:
            temp_list = re.findall("]: (.*?)$", string)

            if temp_list:
                res_str += temp_list[0] + '\n'

        logger.debug(f"prism_api.server_cmd回复：{res_str}")
        return res_str
    else:
        logger.debug(f"prism_api.server_cmd请求对应服务器未开启游戏，返回空值")
        return ''


async def all_server_tellraw(data: dict = []):
    logger.debug(f"prism_api.all_server_tellraw data={data}")
    async with httpx.AsyncClient() as client:
        for server in config['server']:
            await client.post(url=server['url'] + '/tellraw', json=data, timeout=10)
