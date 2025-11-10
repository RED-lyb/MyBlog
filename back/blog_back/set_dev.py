#开发环境配置
DEBUG = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'webproject',
        'USER': 'admin',
        'PASSWORD': '密码',    # 开发时设置数据库密码
        'HOST': '127.0.0.1',  #  默认连接本地数据库
    }
}