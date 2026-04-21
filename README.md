# camera-test

웹캠 영상에서 실시간으로 인물을 탐지하고 **수 / 성별 / 나이 / 자세(서있음·앉음)** 를 분석하여 웹 브라우저에서 확인하는 프로젝트.

자세한 스펙은 [SPEC.md](./SPEC.md) 참고.

## 구조

```
camera-test/
├── backend/    # FastAPI + YOLOv8 + DeepFace (Python)
├── frontend/   # Next.js + WebSocket 클라이언트 (TypeScript)
└── SPEC.md
```

## 빠른 시작

### 백엔드
```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 프론트엔드
```bash
cd frontend
pnpm install
pnpm dev
```

브라우저에서 http://localhost:3000 접속 후 웹캠 권한 허용.

## 개발 단계

- [x] Phase 1 — 사람 탐지 + 바운딩 박스 + 인원수
- [ ] Phase 2 — 성별 / 나이 추정
- [ ] Phase 3 — 자세 분류 (서있음 / 앉음)
- [ ] Phase 4 — CSV 로그 + 대시보드
