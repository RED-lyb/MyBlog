#生产环境配置
import os
DEBUG = False
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'webproject'),
        'USER': os.environ.get('DB_USER', 'admin'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),  # 必须从环境变量设置，不能使用默认值
        'HOST': os.environ.get('DB_HOST', '127.0.0.1'), #如前后端服务器不在同一台服务器，需要修改为实际IP
    }
}