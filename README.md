# MyBlog

## 项目介绍
个人搭建的blog项目

## 软件介绍
1. Vue3
2. Django5.2
3. Python3.12.9


## 安装教程
* 强烈建议按照对应系统版本开始部署，并下载对应版本软件，未尝试跨平台部署，可能存在兼容性问题
### 开发环境安装（Windows10 x64）
* 点击安装node.js
```url
https://nodejs.org/dist/v20.19.4/node-v20.19.4-x64.msi
```
* 点击链接安装Python3.12.9
```url
https://www.python.org/ftp/python/3.12.9/python-3.12.9-amd64.exe
```
* 点击链接安装Mysql
```url
https://dev.mysql.com/get/Downloads/MySQLInstaller/mysql-installer-community-8.0.43.0.msi
```
### 服务器部署（腾讯云服务器OpenCloudOS9）
* 创建项目文件夹并clone仓库源代码
```bash
mkdir /webproject
cd /webproject
git clone https://gitee.com/REDlyb/my-blog.git
```
* 安装开发工具组
```bash
dnf groupinstall "Development Tools" -y
```
* 安装相关依赖
```bash
dnf install zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel libffi-devel xz-devel -y
```
* 创建下载文件夹并下载Python3.12.9
```bash
mkdir /downloads
cd /downloads
wget https://www.python.org/ftp/python/3.12.9/Python-3.12.9.tgz
```
* 解压Python源码
```bash
tar zxvf Python-3.12.9.tgz
cd Python-3.12.9/
```
* 编译安装
```bash
./configure --prefix=/usr/local/python3.12 --enable-optimizations --with-ensurepip=install
make && make altinstall
```
* 创建软链接
```bash
echo 'export PATH=/usr/local/python3.12/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```
* 将pip3.12链接为pip
```bash
ln -s /usr/local/python3.12/bin/pip3.12 /usr/bin/pip
```
* 配置数据库
```bash
dnf update -y
dnf install mariadb-server -y
systemctl start mariadb
systemctl enable mariadb
```
* 设置数据库安全配置
```bash
mysql_secure_installation
```
1. #验证当前root密码
2. n #不启用 unix_socket 认证
3. y #修改数据库root用户密码
4. 输入和确认新密码
5. y #删除匿名用户
6. y #禁止root远程登录
7. y #删除测试数据库
8. y #重新加载数据库

* 登录数据库
```bash
mysql -u root -p
```
* 创建项目数据库
```sql
CREATE DATABASE `webproject` CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_general_ci';
```
* 数据库权限管理配置（创建专门管理web数据库的用户，避免直接使用root用户）
1. 创建允许本地登录的用户（localhost）
```sql
CREATE USER 'admin'@'localhost' IDENTIFIED BY '密码';
```
2. 创建允许远程登录的用户（%表示所有IP，也可指定具体IP如'192.168.1.%'）
```sql
CREATE USER 'admin'@'%' IDENTIFIED BY '密码';
```
3. 授予对webproject数据库的所有权限（本地用户）
```sql
GRANT ALL PRIVILEGES ON webproject.* TO 'admin'@'localhost';
```
4. 授予对webproject数据库的所有权限（远程用户）
```sql
GRANT ALL PRIVILEGES ON webproject.* TO 'admin'@'%';
```
5. 刷新权限使配置生效
```sql
FLUSH PRIVILEGES;
quit;
```
* 修改后端生产环境配置
```bash
vim /webproject/my-blog/back/blog_back/settings.py
```
将CURRENT_ENV = 'dev'改为CURRENT_ENV = 'prod'
```bash
vim /webproject/my-blog/back/blog_back/set_prod.py
```
将PASSWORD与HOST改为实际数据库的密码与服务器地址
* 安装数据库开发工具组和要所用到的依赖
```bash
dnf install mariadb-devel -y
```
* 安装依赖
```bash
cd /webproject/my-blog/back/prod_manage
pip install -r requirements.txt
```
* 安装uwsgi容器
```bash
pip install uwsgi
```
* 运行uwsgi
```bash
uwsgi --ini uwsgi.ini
```
* 安装nginx
```bash
dnf install nginx
vim /etc/nginx/nginx.conf
```
找到server所处位置，并在其中做修改

有域名可以在server_name后添加

修改：
```nginx
root         /usr/share/nginx/html/dist;
```
添加：
```nginx
location / { 

        try_files $uri $uri/ /index.html;

}

location /api/ {
        proxy_pass http://127.0.0.1:8000; #如果前后端不在同一台服务器，则需要修改为对应服务器的ip
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
}
```
* 安装nodejs
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
\. "$HOME/.nvm/nvm.sh"
nvm install 20
```
* 安装项目依赖
```bash
cd /webproject/my-blog/front/blog_front
npm install
```
* 构建项目
```bash
npm run build
```
* 拷贝打包后的文件到nginx目录下
```bash
cp -r /webproject/my-blog/front/blog_front/dist/ /usr/share/nginx/html/
```
* 启动nginx
```bash
systemctl start nginx
```
* 执行上述步骤后即可完成部署

## 参与贡献
1. 李远博