"""InsightFace 기반 얼굴 탐지 + 나이/성별 분석."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np
from insightface.app import FaceAnalysis


def age_to_group(age: int) -> str:
    if age < 10:
        return "under 10"
    return f"{(age // 10) * 10}s"


@dataclass
class FaceAttributes:
    x1: float
    y1: float
    x2: float
    y2: float
    age: int
    gender: str  # "M" or "F"
    det_score: float

    @property
    def age_group(self) -> str:
        return age_to_group(self.age)

    def to_dict(self) -> dict:
        return {
            "x1": round(self.x1, 2),
            "y1": round(self.y1, 2),
            "x2": round(self.x2, 2),
            "y2": round(self.y2, 2),
            "age": int(self.age),
            "age_group": self.age_group,
            "gender": self.gender,
            "det_score": round(self.det_score, 3),
        }

    def center(self) -> Tuple[float, float]:
        return ((self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2)


class FaceAnalyzer:
    def __init__(self, det_size: tuple = (640, 640)) -> None:
        # buffalo_l: detection + age + gender + embedding (first run downloads ~280MB)
        self.app = FaceAnalysis(
            name="buffalo_l",
            providers=["CPUExecutionProvider"],
            allowed_modules=["detection", "genderage"],
        )
        self.app.prepare(ctx_id=0, det_size=det_size)

    def analyze(self, frame: np.ndarray) -> List[FaceAttributes]:
        faces = self.app.get(frame)
        results: List[FaceAttributes] = []
        for f in faces:
            gender_int = int(getattr(f, "gender", 0))
            gender = "M" if gender_int == 1 else "F"
            x1, y1, x2, y2 = [float(v) for v in f.bbox.tolist()]
            results.append(
                FaceAttributes(
                    x1=x1,
                    y1=y1,
                    x2=x2,
                    y2=y2,
                    age=int(round(float(f.age))),
                    gender=gender,
                    det_score=float(f.det_score),
                )
            )
        return results


def match_face_to_person(
    face: FaceAttributes, person_boxes: List[Tuple[float, float, float, float]]
) -> Optional[int]:
    """얼굴 중심이 포함된 첫 번째 person bbox 인덱스를 반환."""
    fx, fy = face.center()
    for i, (x1, y1, x2, y2) in enumerate(person_boxes):
        if x1 <= fx <= x2 and y1 <= fy <= y2:
            return i
    return None
