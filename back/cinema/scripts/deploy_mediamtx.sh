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
用法: deploy_mediamtx.sh [build]

  (无参数)  从 back/cinema/mediamtx 源码编译
  build     同上，强制重新编译

要求:
  - Go 1.26+
  - back/cinema/mediamtx_embed/ 中已提交 VERSION、hls.min.js（无需联网）

说明:
  脚本会将 mediamtx_embed/ 同步到 mediamtx 源码目录后直接 go build，
  不执行 go generate，避免下载 hls.js / 树莓派资源。
  mediamtx 源码已纳入本仓库（back/cinema/mediamtx/），无需单独 clone。
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

build_mediamtx() {
  if [[ ! -f "${MEDIAMTX_SRC}/main.go" ]]; then
    echo "未找到源码: ${MEDIAMTX_SRC}"
    echo "请确认 mediamtx 已置于 back/cinema/mediamtx"
    exit 1
  fi

  if ! command -v go >/dev/null 2>&1; then
    echo "请先安装 Go 1.26+：https://go.dev/dl/"
    exit 1
  fi

  sync_embed_assets

  echo "编译 mediamtx → ${RUNTIME_DIR}"
  mkdir -p "${RUNTIME_DIR}"
  (
    cd "${MEDIAMTX_SRC}"
    CGO_ENABLED=0 go build -o "${BINARY_PATH}" .
  )
}

case "${1:-}" in
  ""|build)
    build_mediamtx
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
