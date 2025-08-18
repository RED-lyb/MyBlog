#生产环境配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'webproject',
        'USER': 'admin',
        'PASSWORD': 'xxx',#生产环境建议修改密码
        'HOST': 'xxx',#改为对应数据库服务器的IP
    }
}