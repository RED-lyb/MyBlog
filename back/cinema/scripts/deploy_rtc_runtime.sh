#!/usr/bin/env bash
# 在 my-blog 仓库内编译 rtc_build，输出到 back/cinema/rtc_runtime
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CINEMA_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
RTC_SRC="${CINEMA_DIR}/rtc_build"
CMAKE_BUILD_DIR="${RTC_SRC}/build"
RUNTIME_DIR="${CINEMA_DIR}/rtc_runtime"

if [[ ! -f "${RTC_SRC}/CMakeLists.txt" ]]; then
  echo "未找到 ${RTC_SRC}，请确认 VolcEngineRTC 源码已置于 back/cinema/rtc_build"
  exit 1
fi

build_rtc() {
  arch="$(uname -m)"
  if [[ "${arch}" != "x86_64" ]]; then
    echo "仅支持 Linux x86_64 编译，当前: ${arch}"
    exit 1
  fi
  echo "编译 rtc_build (Linux x86_64) → ${RUNTIME_DIR}"
  cmake -B"${CMAKE_BUILD_DIR}" -S"${RTC_SRC}"
  cmake --build "${CMAKE_BUILD_DIR}" -j"$(nproc 2>/dev/null || echo 4)"
}

case "${1:-}" in
  build)
    build_rtc
    ;;
  "")
    if [[ -x "${RUNTIME_DIR}/rtccli" ]]; then
      echo "rtccli 已就绪: ${RUNTIME_DIR}/rtccli"
      ls -la "${RUNTIME_DIR}/rtccli" "${RUNTIME_DIR}"/*.so 2>/dev/null | head -20 || true
      exit 0
    fi
    build_rtc
    ;;
  *)
    echo "用法: $0 [build]"
    echo "  (无参数) 若 rtc_runtime 无 rtccli 则编译，否则仅检查"
    echo "  build    强制重新编译"
    exit 1
    ;;
esac

if [[ ! -x "${RUNTIME_DIR}/rtccli" ]]; then
  echo "编译失败：${RUNTIME_DIR}/rtccli 不存在"
  exit 1
fi

echo "完成: ${RUNTIME_DIR}"
ls -la "${RUNTIME_DIR}"
