# Backend (FastAPI + YOLOv8)

## 설치

```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

처음 실행하면 `yolov8n.pt` 가중치가 자동 다운로드됩니다 (약 6MB).

## 실행

```bash
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 엔드포인트

- `GET /health` — 서버 상태 확인
- `WS /ws/analyze` — JPEG 바이너리 프레임을 보내면 분석 결과(JSON) 반환

### WebSocket 응답 예시

```json
{
  "frame": {"width": 640, "height": 480},
  "count": 1,
  "people": [
    {"x1": 120.5, "y1": 80.0, "x2": 380.2, "y2": 470.0, "confidence": 0.91}
  ],
  "inference_ms": 45.2
}
```
