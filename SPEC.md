# 카메라 인물 분석 프로젝트 스펙

## 1. 목표
웹캠 영상에서 실시간으로 인물을 탐지하고, 각 인물의 **수 / 성별 / 나이 / 자세(서있음·앉음)** 를 분석하여 웹 브라우저에서 확인한다.

## 2. 아키텍처 (B안: 백엔드 추론 + 웹 프론트)

```
[웹캠] → [Next.js 프론트] --(WebSocket)--> [FastAPI 백엔드] → [YOLOv8 + DeepFace]
                ↑                                   │
                └───── 분석 결과 (JSON) ←───────────┘
```

- **프론트**: 브라우저에서 `getUserMedia`로 웹캠 프레임 캡처 → WebSocket으로 백엔드에 전송
- **백엔드**: 프레임 수신 → 추론 → 결과(바운딩 박스, 라벨) 전송
- **프론트 렌더**: `<canvas>`로 원본 영상 위에 박스/라벨 오버레이 + 대시보드 숫자 표시
- 실행 범위: **로컬(localhost)**, 본인 1명 사용, 단일 카메라

## 3. 기술 스택

### 백엔드 (Python)
- FastAPI + `uvicorn` (WebSocket)
- **YOLOv8** (`ultralytics`) — 사람 탐지 + 자세 추정(pose keypoints)
- **InsightFace** (buffalo_l, ONNX Runtime) — 얼굴 탐지 + 나이/성별 추정
  - 초기 계획 DeepFace에서 변경: macOS ARM의 TensorFlow 설치 복잡도와 나이 추정 정확도 이점 때문에 교체
- OpenCV — 프레임 디코딩
- Python 3.11

### 프론트 (Web)
- Next.js 14 (App Router) + TypeScript
- React + Tailwind CSS
- WebSocket 클라이언트
- `<canvas>` 오버레이

### 개발 환경
- macOS (M1/M2/M3 가정, MPS 가속)
- 패키지: uv (Python), pnpm (Node)

## 4. 기능 상세 (MVP → 확장)

### Phase 1 (MVP)
- [ ] 웹캠 프레임 캡처 → 백엔드 전송
- [ ] YOLOv8로 사람 탐지 → **사람 수** 표시
- [ ] 프론트에 바운딩 박스 오버레이

### Phase 2 (얼굴 속성)
- [ ] 각 인물 얼굴 영역 크롭 → DeepFace로 **성별 / 나이 추정**
- [ ] 나이는 **10대 단위 구간**으로 표시 (예: `20s`, `30s`)
- [ ] 라벨에 `Male, 20s` 형식으로 표시

### Phase 3 (자세 분류)
- [ ] YOLOv8 Pose로 17개 키포인트 추출
- [ ] 간단한 규칙 기반 분류: 엉덩이-무릎-발목 각도로 **서있음 / 앉음** 판정
- [ ] 라벨에 `Standing` / `Sitting` 추가

### Phase 4 (로그 & 대시보드)
- [ ] 프레임별 분석 결과를 **CSV 로그**로 저장 (`timestamp, person_id, gender, age_group, posture`)
- [ ] 대시보드: 현재 인원, 성별 분포, 자세 분포 (간단한 카운터 + 막대)

### 비포함 (나중에)
- 동일 인물 추적(ID 유지) — Phase 5 이후
- 얼굴 이미지 저장 (프라이버시 이슈) — **메타데이터만 저장**
- 다중 카메라, IP 카메라, 원격 접속

## 5. 성능 목표

- **분석 FPS**: 3~5 FPS (실시간성은 적당히, 정확도 우선)
- **영상 표시 FPS**: 30 FPS (분석 결과는 낮은 FPS, 영상은 부드럽게)
- 지연: ~300ms 이내 목표

## 6. 프로젝트 구조 (예정)

```
camera-test/
├── backend/
│   ├── pyproject.toml
│   ├── app/
│   │   ├── main.py          # FastAPI + WebSocket 엔드포인트
│   │   ├── detector.py      # YOLOv8 래퍼
│   │   ├── face_analyzer.py # DeepFace 래퍼
│   │   ├── posture.py       # 자세 분류 로직
│   │   └── logger.py        # CSV 로그
│   └── logs/
├── frontend/
│   ├── package.json
│   ├── app/
│   │   └── page.tsx         # 카메라 + 오버레이 + 대시보드
│   └── components/
│       ├── CameraView.tsx
│       └── Dashboard.tsx
├── SPEC.md                  # 이 문서
└── README.md
```

## 7. 검증 계획 (Phase별)

| Phase | 테스트 방법 | 기대 결과 |
|-------|------------|----------|
| 1 | 본인이 카메라 앞에 서기 | 화면에 1명 + 박스 표시 |
| 1 | 2명이 같이 등장 | "2 people" 표시 |
| 2 | 본인 얼굴이 잡힐 때 | 성별/나이 라벨 표시 |
| 3 | 의자에 앉기 → 일어서기 | `Sitting` ↔ `Standing` 전환 |
| 4 | 1분간 실행 | `logs/YYYYMMDD.csv` 생성 확인 |

## 8. 열린 질문 / 리스크

- **DeepFace 나이 추정 정확도**: 종종 크게 틀립니다. 대안으로 InsightFace로 교체 가능.
- **자세 분류 정확도**: 규칙 기반은 경계 케이스(쪼그려 앉기 등)에 약함. 필요 시 pose classifier 모델로 교체.
- **브라우저 → 백엔드 프레임 전송 포맷**: JPEG base64 vs binary. 일단 **JPEG binary**로 시작.
- **macOS 웹캠 권한**: 브라우저에서 허용 필요.

---

## ✅ 확인 요청
이 스펙대로 진행해도 괜찮을까요? 수정하고 싶은 부분 있으면 알려주세요.
확정되면 **Phase 1 (MVP)** 부터 구현 시작합니다.
