"""얼굴이 포함된 테스트 이미지로 WebSocket 응답 확인.

공개된 샘플 인물 사진(저작권 free)을 프로그래매틱으로 가져와 분석.
"""
from __future__ import annotations

import asyncio
import json
import urllib.request

import cv2
import numpy as np
import websockets

# Ultralytics 공식 샘플(사람 얼굴 포함)
SAMPLE_URL = "https://ultralytics.com/images/bus.jpg"


def fetch_jpeg() -> bytes:
    with urllib.request.urlopen(SAMPLE_URL, timeout=10) as r:
        return r.read()


async def main() -> None:
    jpeg_bytes = fetch_jpeg()
    async with websockets.connect("ws://127.0.0.1:8000/ws/analyze") as ws:
        # 첫 호출은 warmup
        await ws.send(jpeg_bytes)
        _ = await asyncio.wait_for(ws.recv(), timeout=60)
        # 두 번째 호출로 실제 측정
        await ws.send(jpeg_bytes)
        resp = await asyncio.wait_for(ws.recv(), timeout=60)
        data = json.loads(resp)
        print(json.dumps(data, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
