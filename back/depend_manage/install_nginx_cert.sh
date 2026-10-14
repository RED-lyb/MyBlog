#!/usr/bin/env bash
# sudo /webproject/my-blog/back/depend_manage/install_nginx_cert.sh
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
BACK_DIR=$(cd "$SCRIPT_DIR/.." && pwd)
ZIP_PATH="$BACK_DIR/api/nginx_cert/inbox/lybandljy.cn_nginx.zip"

# -j 去掉压缩包里的目录，四个文件直接落到 /etc/nginx
unzip -o -j "$ZIP_PATH" -d /etc/nginx
rm -rf /etc/nginx/lybandljy.cn.csr /etc/nginx/lybandljy.cn_bundle.pem
systemctl reload nginx
rm -rf "$ZIP_PATH"
