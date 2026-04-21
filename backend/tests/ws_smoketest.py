"""WebSocket smoke test — 합성 이미지를 한 장 보내고 응답을 확인."""
from __future__ import annotations

import asyncio
import json

import cv2
import numpy as np
import websockets


async def main() -> None:
    img = np.full((480, 640, 3), 60, dtype=np.uint8)
    cv2.rectangle(img, (200, 100), (440, 440), (200, 200, 200), -1)
    ok, buf = cv2.imencode(".jpg", img)
    assert ok
    async with websockets.connect("ws://127.0.0.1:8000/ws/analyze") as ws:
        await ws.send(buf.tobytes())
        response = await asyncio.wait_for(ws.recv(), timeout=30)
        print(json.dumps(json.loads(response), indent=2))


if __name__ == "__main__":
    asyncio.run(main())
