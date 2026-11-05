#!/bin/bash

set -a
source "$(dirname "$0")/.env"
set +a

PROGRESS_FILE=$(mktemp /tmp/aws-relay-progress.XXXXXX)
FFMPEG_PID=""

cleanup() {
  trap - EXIT TERM INT

  if [ -n "$FFMPEG_PID" ]; then
    kill "$FFMPEG_PID" 2>/dev/null || true

    for i in 1 2 3 4 5; do
      kill -0 "$FFMPEG_PID" 2>/dev/null || break
      sleep 1
    done

    kill -9 "$FFMPEG_PID" 2>/dev/null || true
    wait "$FFMPEG_PID" 2>/dev/null || true
  fi

  rm -f "$PROGRESS_FILE"
}

trap cleanup EXIT
trap 'exit 0' TERM INT

# AWS MediaMTX로 RTSP 영상 재송출
ffmpeg \
  -nostdin \
  -stats_period 2 \
  -progress "$PROGRESS_FILE" \
  -rtsp_transport tcp \
  -timeout 10000000 \
  -i rtsp://127.0.0.1:8554/cam \
  -c copy \
  -f rtsp \
  -rtsp_transport tcp \
  -timeout 10000000 \
  "rtsp://${RTSP_USER}:${RTSP_PASSWORD}@${AWS_PUBLIC_IP}:8554/cam" &

FFMPEG_PID=$!

LAST_FRAME=0
LAST_PROGRESS=$SECONDS

# 5초마다 FFmpeg 영상 송출 진행 상태 확인
while kill -0 "$FFMPEG_PID" 2>/dev/null; do
  sleep 5

  CURRENT_FRAME=$(
    grep '^frame=' "$PROGRESS_FILE" 2>/dev/null |
    tail -n 1 |
    cut -d= -f2 |
    tr -d ' '
  )

  if [[ "$CURRENT_FRAME" =~ ^[0-9]+$ ]]; then
    if (( CURRENT_FRAME > LAST_FRAME )); then
      LAST_FRAME=$CURRENT_FRAME
      LAST_PROGRESS=$SECONDS
    fi
  fi

  # 40초 동안 프레임이 증가하지 않으면 재시작
  if (( SECONDS - LAST_PROGRESS >= 40 )); then
    echo "영상 송출 정체 감지 - FFmpeg 자동 재시작"
    exit 1
  fi
done

wait "$FFMPEG_PID"
exit $?
