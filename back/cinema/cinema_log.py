"""同频影院日志，统一写入 log/back.log（由现有后端轮转策略管理）"""
from datetime import datetime

from .mediamtx_config import BLOG_LOG_FILE, LOG_DIR


def cinema_log(message, tag='cinema'):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f'[{ts}] [{tag}] {message}\n'
    with open(BLOG_LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(line)
