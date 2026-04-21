"""FastAPI 엔드포인트 — WebSocket으로 프레임 받고 분석 결과 반환."""
from __future__ import annotations

import asyncio
import time

import cv2
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.detector import PersonDetector

app = FastAPI(title="camera-test backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

detector = PersonDetector()


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


def _decode_jpeg(data: bytes) -> np.ndarray | None:
    arr = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    return img


@app.websocket("/ws/analyze")
async def websocket_analyze(ws: WebSocket) -> None:
    await ws.accept()
    try:
        while True:
            data = await ws.receive_bytes()
            frame = await asyncio.to_thread(_decode_jpeg, data)
            if frame is None:
                await ws.send_json({"error": "invalid_frame"})
                continue

            t0 = time.perf_counter()
            detections = await asyncio.to_thread(detector.detect, frame)
            elapsed_ms = (time.perf_counter() - t0) * 1000

            h, w = frame.shape[:2]
            await ws.send_json(
                {
                    "frame": {"width": int(w), "height": int(h)},
                    "count": len(detections),
                    "people": [d.to_dict() for d in detections],
                    "inference_ms": round(elapsed_ms, 1),
                }
            )
    except WebSocketDisconnect:
        return
