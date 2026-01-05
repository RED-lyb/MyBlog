# MyBlog

## 项目介绍
个人搭建的blog项目

## 主要软件介绍
1. Vue3
2. Django5.2


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
* 安装后端依赖
```bash
cd my-blog/back/depend_manage
pip install -r requirements.txt
```
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
GRANT PROCESS ON *.* TO 'admin'@'localhost';
```
4. 授予对webproject数据库的所有权限（远程用户）
```sql
GRANT ALL PRIVILEGES ON webproject.* TO 'admin'@'%';
GRANT PROCESS ON *.* TO 'admin'@'%';
```
5. 刷新权限使配置生效
```sql
FLUSH PRIVILEGES;
quit;
```
* 导入数据库结构
```bash
cd my-blog/back/depend_manage
mysql -u admin -p webproject < ./webproject.sql
```
* 初始化首个用户（创建第一个管理员用户，同时也是作者用户）
```bash
# 注意：
# 1. 密码需符合规则：至少8位，包含数字、大写字母、小写字母
# 2. 密保答案只能包含中文、英文和数字
# 3. 用户名不能使用数据库保留字（如SELECT、INSERT等）
cd my-blog/back/depend_manage
python init_admin_user.py <用户名> <密码> <密保问题> <密保答案>
```
* 修改webproject\back\blog_back\set_dev.py
  * 将['PASSWORD': '密码',]改为自己配置的数据库密码
* 安装前端依赖
```bash
cd my-blog/front/blog_front  #找到项目根目录并进入前端目录
npm install
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
2. N  #不启用 unix_socket 认证
3. Y  #修改数据库root用户密码
4. 输入和确认新密码
5. Y  #删除匿名用户
6. Y  #禁止root远程登录
7. Y  #删除测试数据库
8. Y  #重新加载数据库

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
* 导入数据库字段
```bash
mysql -u admin -p webproject < /webproject/my-blog/back/depend_manage/webproject.sql
```
* 初始化管理员用户（创建第一个管理员用户，同时也是作者用户）
```bash
# 注意：
# 1. 密码需符合规则：至少8位，包含数字、大写字母、小写字母
# 2. 密保答案只能包含中文、英文和数字
# 3. 用户名不能使用数据库保留字（如SELECT、INSERT等）
cd /webproject/my-blog/back/depend_manage
python3.12 init_admin_user.py <用户名> <密码> <密保问题> <密保答案>
```
* 安装数据库开发工具组和要所用到的依赖
```bash
dnf install mariadb-devel -y
```
* 安装依赖
```bash
pip install -r /webproject/my-blog/back/depend_manage/requirements.txt
```
* 配置环境变量
1. 生成 Secret Key：
```bash
# 一定要复制或记录输出值，后续需要填入.env文件
python3.12 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
2. 在 `/webproject/my-blog/back/blog_back/` 目录下创建 `.env` 文件：
```bash
vim /webproject/my-blog/back/blog_back/.env
```
3. 填入生产环境配置：
```bash
# Django Secret Key（填入上述Secret Key值）
DJANGO_SECRET_KEY=

# 数据库连接配置（必须根据实际值进行配置）
DB_NAME=webproject
DB_USER=admin
DB_PASSWORD=密码
DB_HOST=127.0.0.1  # 或数据库服务器的实际IP
```
4. 修改后端环境引用：
```bash
vim /webproject/my-blog/back/blog_back/settings.py
```
将 `CURRENT_ENV = 'dev'` 改为 `CURRENT_ENV = 'prod'`
* 安装uwsgi容器
```bash
pip install uwsgi
```
* 运行uwsgi
```bash
uwsgi --ini /webproject/my-blog/back/depend_manage/uwsgi.ini
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
client_max_body_size 300M; #上传文件大小限制，可按实际需求进行修改。

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
* 执行上述步骤后即可完成部署，可通过访问服务器IP或域名进行访问。

## 网盘容量自动管理脚本配置
* 编辑 crontab：
```bash
crontab -e
```
* 添加以下行（每天0:00执行）：
```bash
0 0 * * * cd /webproject/my-blog/back && /usr/local/python3.12/bin/python3.12 manage.py cleanup_old_files >/dev/null 2>&1
```
* `--days [(int)天数]`: 指定删除多少天前修改的文件（不带该参数则默认7天）
* `--dry-run`: 预览模式，仅显示将要删除的文件，不实际删除
* `--no-log`: 不写入日志文件，仅输出到控制台（默认情况下会同时输出到控制台和日志文件）

## 参与贡献
1. 李远博