# MyBlog

## 项目介绍
个人搭建的blog项目

## 软件介绍
1. Vue3
2. Django5.2
3. Python3.12.9


## 安装教程
### 服务器部署（腾讯云OpenCloudOS9）
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

## 使用说明

1.  xxxx
2.  xxxx
3.  xxxx

## 参与贡献
1. 李远博