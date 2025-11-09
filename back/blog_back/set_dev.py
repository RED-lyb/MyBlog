#开发环境配置
import os
DEBUG = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'webproject'),
        'USER': os.environ.get('DB_USER', 'admin'),
        'PASSWORD': os.environ.get('DB_PASSWORD', '123456'),  # 从环境变量读取，默认值仅用于开发
        'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
    }
}