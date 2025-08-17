#开发环境配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'webproject',
        'USER': 'root',
        'PASSWORD': '123456',#生产环境建议修改密码
        'HOST': '127.0.0.1',
    }
}