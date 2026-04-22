"""YOLOv8 기반 사람 탐지 + 추적 래퍼."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import numpy as np
from ultralytics import YOLO

PERSON_CLASS_ID = 0


@dataclass
class Detection:
    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float
    track_id: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            "x1": round(self.x1, 2),
            "y1": round(self.y1, 2),
            "x2": round(self.x2, 2),
            "y2": round(self.y2, 2),
            "confidence": round(self.confidence, 3),
            "track_id": self.track_id,
        }


class PersonDetector:
    def __init__(
        self,
        model_name: str = "yolov8n.pt",
        conf: float = 0.4,
        tracker: str = "botsort.yaml",
    ) -> None:
        self.model = YOLO(model_name)
        self.conf = conf
        self.tracker = tracker

    def _parse(self, results) -> List[Detection]:
        detections: List[Detection] = []
        if not results:
            return detections
        boxes = results[0].boxes
        if boxes is None or len(boxes) == 0:
            return detections
        xyxy = boxes.xyxy.cpu().numpy()
        confs = boxes.conf.cpu().numpy()
        ids = boxes.id.cpu().numpy() if boxes.id is not None else None
        for i, ((x1, y1, x2, y2), c) in enumerate(zip(xyxy, confs)):
            tid = int(ids[i]) if ids is not None else None
            detections.append(
                Detection(float(x1), float(y1), float(x2), float(y2), float(c), tid)
            )
        return detections

    def detect(self, frame: np.ndarray) -> List[Detection]:
        results = self.model.predict(
            frame,
            classes=[PERSON_CLASS_ID],
            conf=self.conf,
            verbose=False,
        )
        return self._parse(results)

    def track(self, frame: np.ndarray) -> List[Detection]:
        results = self.model.track(
            frame,
            classes=[PERSON_CLASS_ID],
            conf=self.conf,
            persist=True,
            tracker=self.tracker,
            verbose=False,
        )
        return self._parse(results)
