"""FastAPI 엔드포인트 — WebSocket으로 프레임 받고 분석 결과 반환."""
from __future__ import annotations

import asyncio
import time

import cv2
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.detector import PersonDetector
from app.face_analyzer import FaceAnalyzer, match_face_to_person

app = FastAPI(title="camera-test backend", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

person_detector = PersonDetector()
face_analyzer = FaceAnalyzer()


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


def _decode_jpeg(data: bytes) -> np.ndarray | None:
    arr = np.frombuffer(data, dtype=np.uint8)
    return cv2.imdecode(arr, cv2.IMREAD_COLOR)


def _analyze_frame(frame: np.ndarray) -> dict:
    t0 = time.perf_counter()
    people = person_detector.detect(frame)
    t_person = (time.perf_counter() - t0) * 1000

    t1 = time.perf_counter()
    faces = face_analyzer.analyze(frame)
    t_face = (time.perf_counter() - t1) * 1000

    person_boxes = [(p.x1, p.y1, p.x2, p.y2) for p in people]
    attached: dict[int, dict] = {}
    unassigned_faces: list[dict] = []
    for face in faces:
        idx = match_face_to_person(face, person_boxes)
        face_dict = {
            "age": face.age,
            "age_group": face.age_group,
            "gender": face.gender,
            "det_score": round(face.det_score, 3),
        }
        if idx is None:
            unassigned_faces.append({**face_dict, **{
                "x1": round(face.x1, 2), "y1": round(face.y1, 2),
                "x2": round(face.x2, 2), "y2": round(face.y2, 2),
            }})
        else:
            prev = attached.get(idx)
            if prev is None or face.det_score > prev["det_score"]:
                attached[idx] = face_dict

    people_payload = []
    for i, p in enumerate(people):
        entry = p.to_dict()
        entry["face"] = attached.get(i)
        people_payload.append(entry)

    h, w = frame.shape[:2]
    return {
        "frame": {"width": int(w), "height": int(h)},
        "count": len(people),
        "people": people_payload,
        "unassigned_faces": unassigned_faces,
        "inference_ms": {
            "person": round(t_person, 1),
            "face": round(t_face, 1),
        },
    }


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
            payload = await asyncio.to_thread(_analyze_frame, frame)
            await ws.send_json(payload)
    except WebSocketDisconnect:
        return
