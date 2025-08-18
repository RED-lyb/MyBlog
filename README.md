# MyBlog

## 项目介绍
个人搭建的blog项目

## 软件介绍
1. Vue3
2. Django5.2
3. Python3.12.9


## 安装教程

### 服务器部署（腾讯云服务器OpenCloudOS9）

* 创建项目文件夹并clone仓库源代码

mkdir /webproject

cd /webproject

git clone https://gitee.com/REDlyb/my-blog.git

* 安装开发工具组

dnf groupinstall "Development Tools" -y

* 安装相关依赖

dnf install zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel libffi-devel xz-devel -y

* 创建下载文件夹并下载Python3.12.9

mkdir /downloads

cd /downloads

wget https://www.python.org/ftp/python/3.12.9/Python-3.12.9.tgz

* 解压Python源码

tar zxvf Python-3.12.9.tgz

cd Python-3.12.9/

* 编译安装

./configure --prefix=/usr/local/python3.12 --enable-optimizations --with-ensurepip=install

make && make altinstall

* 创建软链接

echo 'export PATH=/usr/local/python3.12/bin:$PATH' >> ~/.bashrc

source ~/.bashrc

* 将pip3.12链接为pip

ln -s /usr/local/python3.12/bin/pip3.12 /usr/bin/pip

* 配置数据库

dnf update -y

dnf install mariadb-server -y

systemctl start mariadb

systemctl enable mariadb

* 设置数据库安全配置

mysql_secure_installation

1. #验证当前root密码
2. n #不启用 unix_socket 认证
3. y #修改数据库root用户密码
4. 输入和确认新密码
5. y #删除匿名用户
6. y #禁止root远程登录
7. y #删除测试数据库
8. y #重新加载数据库

* 数据库权限管理配置（创建专门管理web数据库的用户，避免直接使用root用户）

1. 创建允许本地登录的用户（localhost）

CREATE USER 'admin'@'localhost' IDENTIFIED BY '密码';

2. 创建允许远程登录的用户（%表示所有IP，也可指定具体IP如'192.168.1.%'）

CREATE USER 'admin'@'%' IDENTIFIED BY '密码';

3. 授予对webproject数据库的所有权限（本地用户）

GRANT ALL PRIVILEGES ON webproject.* TO 'admin'@'localhost';

4. 授予对webproject数据库的所有权限（远程用户）

GRANT ALL PRIVILEGES ON webproject.* TO 'admin'@'%';

5. 刷新权限使配置生效

FLUSH PRIVILEGES;

* 安装数据库开发工具组和要所用到的依赖

dnf install mariadb-devel -y

cd /webproject/my-blog/back/prod_manage

* 安装依赖

pip install -r requirements.txt

* 安装uwsgi容器

pip install uwsgi

* 运行uwsgi

uwsgi --ini uwsgi.ini

* 安装nginx
dnf install nginx

systemctl status nginx.service

cd /

* 安装nodejs

curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash

\. "$HOME/.nvm/nvm.sh"

nvm install 20

cd /webproject/my-blog/front/blog_front

* 安装项目依赖


npm install

npm run build

### 数据库搭建

CREATE DATABASE `webproject` CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_general_ci';


## 参与贡献
1. 李远博