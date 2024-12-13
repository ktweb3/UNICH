import asyncio
import json
from datetime import datetime
import aiohttp
import colorama

# 初始化颜色支持
colorama.init()

# 日志格式化
def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log(level, message):
    color = {
        'INFO': colorama.Fore.GREEN,
        'WARN': colorama.Fore.YELLOW,
        'ERROR': colorama.Fore.RED
    }.get(level, colorama.Fore.WHITE)
    print(f"{color}[{now()}] [{level}]: {colorama.Style.RESET_ALL}{message}")

# 从文件读取token
async def read_tokens(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file if line.strip()]
    except Exception as e:
        log('ERROR', f'读取tokens.txt时出错：{str(e)}')
        return []

# 开始挖矿
async def start_mining(session, token):
    url = 'https://api.unich.com/airdrop/user/v1/mining/start'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    try:
        async with session.post(url, headers=headers, json={}) as response:
            response.raise_for_status()
            data = await response.json()
            log('INFO', f'成功开始挖矿：{json.dumps(data)}')
    except aiohttp.ClientResponseError as e:
        log('ERROR', f'开始挖矿时出错：{e.message}')
    except Exception as e:
        log('ERROR', f'开始挖矿时出错：{str(e)}')

# 获取用户社交任务列表
async def get_social_list_by_user(session, token):
    url = 'https://api.unich.com/airdrop/user/v1/social/list-by-user'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    try:
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()
            data = await response.json()
            return data.get('data', None)
    except aiohttp.ClientResponseError as e:
        log('ERROR', f'获取社交任务列表时出错：{e.message}')
        return None
    except Exception as e:
        log('ERROR', f'获取社交任务列表时出错：{str(e)}')
        return None

# 获取最近的挖矿数据
async def get_recent_mining(session, token):
    url = 'https://api.unich.com/airdrop/user/v1/mining/recent'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    try:
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientResponseError as e:
        log('ERROR', f'获取最近挖矿数据时出错：{e.message}')
        return None
    except Exception as e:
        log('ERROR', f'获取最近挖矿数据时出错：{str(e)}')
        return None

# 领取社交奖励
async def claim_social_reward(session, token, task_id):
    url = f'https://api.unich.com/airdrop/user/v1/social/claim/{task_id}'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {"evidence": task_id}
    try:
        async with session.post(url, headers=headers, json=payload) as response:
            response.raise_for_status()
            data = await response.json()
            log('INFO', f'领取成功：{json.dumps(data)}')
    except aiohttp.ClientResponseError as e:
        log('ERROR', f'领取奖励时出错：{e.message}')
    except Exception as e:
        log('ERROR', f'领取奖励时出错：{str(e)}')

# 主函数
async def start():
    banner = """
               ╔═╗╔═╦╗─╔╦═══╦═══╦═══╦═══╗
               ╚╗╚╝╔╣║─║║╔══╣╔═╗║╔═╗║╔═╗║
               ─╚╗╔╝║║─║║╚══╣║─╚╣║─║║║─║║
               ─╔╝╚╗║║─║║╔══╣║╔═╣╚═╝║║─║║
               ╔╝╔╗╚╣╚═╝║╚══╣╚╩═║╔═╗║╚═╝║
               ╚═╝╚═╩═══╩═══╩═══╩╝─╚╩═══╝
               我的gihub：github.com/Gzgod
               我的推特：推特雪糕战神@Hy78516012
               我的频道：t.me/xuegaoz
    """
    log('INFO', banner)
    tokens = await read_tokens('tokens.txt')

    async with aiohttp.ClientSession() as session:
        while True:
            for token in tokens:
                recent = await get_recent_mining(session, token)
                is_mining = recent.get('data', {}).get('isMining', False) if recent else False
                balance = recent.get('data', {}).get('mUn', 0) if recent else 0
                log('INFO', f'挖矿状态：{is_mining} | 总积分：{balance}')

                if not is_mining:
                    await start_mining(session, token)
                else:
                    log('INFO', '已经在挖矿中。')

                tasks = await get_social_list_by_user(session, token)
                if tasks:
                    unclaimed_ids = [item['id'] for item in tasks.get('items', []) if not item.get('claimed', True)]
                    log('INFO', f'发现 {len(unclaimed_ids)} 个未领取任务')
                    for task_id in unclaimed_ids:
                        log('INFO', f'尝试完成任务 ID: {task_id}')
                        await claim_social_reward(session, token, task_id)

            log('WARN', '冷却一小时后重新检查...')
            await asyncio.sleep(3600)  # 等待一小时

# 运行主函数
if __name__ == "__main__":
    asyncio.run(start())
