"""
配置文件读取工具
用于读取后端配置文件 config_back.json
"""
import json
from pathlib import Path
from django.conf import settings


def get_config_path():
    """
    获取配置文件路径
    """
    return Path(settings.BASE_DIR) / 'config' / 'config_back.json'


def load_config():
    """
    加载配置文件
    如果文件不存在或读取失败，返回默认配置
    """
    config_path = get_config_path()
    
    # 默认配置
    default_config = {
        # 网盘清理配置
        'network_disk': {
            'cleanup_days': 7  # 删除多少天前的文件
        },
        # 验证码配置
        'captcha': {
            'challenge_funct': 'captcha.helpers.random_char_challenge',
            'length': 4,
            'timeout': 5,  # 验证码有效期（分钟）
            'image_size': [120, 40],
            'font_size': 20,
            'background_color': '#ffffff',
            'foreground_color': '#001100',
            'noise_functions': ['captcha.helpers.noise_arcs', 'captcha.helpers.noise_dots']
        },
        # JWT Token配置
        'jwt': {
            'access_token_expire_minutes': 60,  # Access Token 60分钟
            'refresh_token_expire_days': 30  # Refresh Token 30天
        }
    }
    
    if not config_path.exists():
        # 如果配置文件不存在，创建默认配置
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=4)
        except Exception:
            pass
        return default_config
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # 合并默认配置，确保所有字段都存在
        def merge_config(default, user):
            """递归合并配置"""
            result = default.copy()
            for key, value in user.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = merge_config(result[key], value)
                else:
                    result[key] = value
            return result
        
        return merge_config(default_config, config_data)
    except Exception:
        # 读取失败，返回默认配置
        return default_config


def get_config_value(key_path, default=None):
    """
    获取配置值
    key_path: 配置键路径，如 'network_disk.cleanup_days'
    default: 默认值
    """
    config = load_config()
    keys = key_path.split('.')
    value = config
    
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    
    return value


def save_config(config_data):
    """
    保存配置文件
    """
    config_path = get_config_path()
    
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f'保存配置文件失败: {str(e)}')
        return False

