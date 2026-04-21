"""YOLOv8 기반 사람 탐지 래퍼."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

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

    def to_dict(self) -> dict:
        return {
            "x1": round(self.x1, 2),
            "y1": round(self.y1, 2),
            "x2": round(self.x2, 2),
            "y2": round(self.y2, 2),
            "confidence": round(self.confidence, 3),
        }


class PersonDetector:
    def __init__(self, model_name: str = "yolov8n.pt", conf: float = 0.4) -> None:
        self.model = YOLO(model_name)
        self.conf = conf

    def detect(self, frame: np.ndarray) -> List[Detection]:
        results = self.model.predict(
            frame,
            classes=[PERSON_CLASS_ID],
            conf=self.conf,
            verbose=False,
        )
        detections: List[Detection] = []
        if not results:
            return detections
        boxes = results[0].boxes
        if boxes is None:
            return detections
        xyxy = boxes.xyxy.cpu().numpy()
        confs = boxes.conf.cpu().numpy()
        for (x1, y1, x2, y2), c in zip(xyxy, confs):
            detections.append(Detection(float(x1), float(y1), float(x2), float(y2), float(c)))
        return detections
