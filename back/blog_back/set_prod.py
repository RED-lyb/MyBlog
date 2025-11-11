#生产环境配置
import os
from dotenv import load_dotenv
load_dotenv()
# 从环境变量加载配置，生产环境必须设置所有配置项
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')  # 生产环境必须设置，无默认值
if not SECRET_KEY:
    raise ValueError("生产环境必须设置 DJANGO_SECRET_KEY 环境变量")

DEBUG = False
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'webproject'),
        'USER': os.environ.get('DB_USER', 'admin'),
        'PASSWORD': os.environ.get('DB_PASSWORD', '密码'),
        'HOST': os.environ.get('DB_HOST', '127.0.0.1'), #如前后端服务器不在同一台服务器，需要修改为实际IP
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES', default_storage_engine=INNODB, collation_connection=utf8mb4_unicode_ci"
        }
    }

}
# 验证生产环境必需的数据库密码是否已设置
if not DATABASES['default']['PASSWORD']:
    raise ValueError("生产环境必须设置 DB_PASSWORD 环境变量")
