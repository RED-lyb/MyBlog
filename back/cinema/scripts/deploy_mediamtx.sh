#!/usr/bin/env bash
# 从源码编译 mediamtx，输出到 back/cinema/mediamtx_runtime
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CINEMA_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
MEDIAMTX_SRC="${CINEMA_DIR}/mediamtx"
EMBED_DIR="${CINEMA_DIR}/mediamtx_embed"
RUNTIME_DIR="${CINEMA_DIR}/mediamtx_runtime"
BINARY_PATH="${RUNTIME_DIR}/mediamtx"

VERSION_SRC="${EMBED_DIR}/VERSION"
HLS_SRC="${EMBED_DIR}/hls.min.js"
VERSION_DST="${MEDIAMTX_SRC}/internal/core/VERSION"
HLS_DST="${MEDIAMTX_SRC}/internal/servers/hls/hls.min.js"

usage() {
  cat <<'EOF'
用法: deploy_mediamtx.sh [build|vendor]

  (无参数)  从 back/cinema/mediamtx 源码编译
  build     同上，强制重新编译
  vendor    把 Go 依赖下载到 mediamtx/vendor/（只需联网一次）

要求:
  - Go 1.26+
  - back/cinema/mediamtx_embed/ 中已提交 VERSION、hls.min.js（无需联网）

说明:
  脚本会将 mediamtx_embed/ 同步到 mediamtx 源码目录后直接 go build，
  不执行 go generate，避免下载 hls.js / 树莓派资源。
  mediamtx 源码已纳入本仓库（back/cinema/mediamtx/），无需单独 clone。

  go build 会按 go.mod 拉取 WebRTC/RTSP 等第三方库。国内可先：
    export GOPROXY=https://goproxy.cn,direct
  有网的机器上执行 ./deploy_mediamtx.sh vendor，把 mediamtx/vendor/ 拷到
  服务器同路径后，再编译会走 -mod=vendor，不再访问网络。
EOF
}

sync_embed_assets() {
  if [[ ! -f "${VERSION_SRC}" || ! -f "${HLS_SRC}" ]]; then
    echo "缺少嵌入资源，请确保以下文件已提交到仓库："
    echo "  ${VERSION_SRC}"
    echo "  ${HLS_SRC}"
    exit 1
  fi

  mkdir -p "$(dirname "${VERSION_DST}")" "$(dirname "${HLS_DST}")"
  cp "${VERSION_SRC}" "${VERSION_DST}"
  cp "${HLS_SRC}" "${HLS_DST}"
  echo "已同步嵌入资源:"
  echo "  ${VERSION_SRC} → ${VERSION_DST}"
  echo "  ${HLS_SRC} → ${HLS_DST}"
}

require_go_and_src() {
  if [[ ! -f "${MEDIAMTX_SRC}/main.go" ]]; then
    echo "未找到源码: ${MEDIAMTX_SRC}"
    echo "请确认 mediamtx 已置于 back/cinema/mediamtx"
    exit 1
  fi

  if ! command -v go >/dev/null 2>&1; then
    echo "请先安装 Go 1.26+：https://go.dev/dl/"
    exit 1
  fi
}

vendor_mediamtx() {
  require_go_and_src
  echo "下载 Go 依赖到 ${MEDIAMTX_SRC}/vendor"
  (
    cd "${MEDIAMTX_SRC}"
    go mod vendor
  )
  echo "完成: ${MEDIAMTX_SRC}/vendor"
  echo "把该目录同步到编译机同路径后，再执行 ./deploy_mediamtx.sh 即可离线编译。"
}

build_mediamtx() {
  require_go_and_src
  sync_embed_assets

  echo "编译 mediamtx → ${RUNTIME_DIR}"
  mkdir -p "${RUNTIME_DIR}"
  (
    cd "${MEDIAMTX_SRC}"
    if [[ -d vendor ]]; then
      echo "使用本地 vendor/ 离线编译"
      CGO_ENABLED=0 go build -mod=vendor -o "${BINARY_PATH}" .
    else
      echo "未找到 vendor/，将按 GOPROXY 拉取依赖"
      CGO_ENABLED=0 go build -o "${BINARY_PATH}" .
    fi
  )
}

case "${1:-}" in
  ""|build)
    build_mediamtx
    ;;
  vendor)
    vendor_mediamtx
    exit 0
    ;;
  -h|--help|help)
    usage
    exit 0
    ;;
  *)
    usage
    exit 1
    ;;
esac

if [[ ! -x "${BINARY_PATH}" ]]; then
  echo "编译失败：${BINARY_PATH} 不存在"
  exit 1
fi

echo "完成: ${BINARY_PATH}"
