# Frontend (Next.js)

## 설치

```bash
cd frontend
pnpm install
```

## 실행

```bash
pnpm dev
```

브라우저에서 http://localhost:3000 접속 후 웹캠 권한 허용.

백엔드 URL을 바꾸려면 `.env.local`에 `NEXT_PUBLIC_WS_URL` 설정.

## 구조

- `app/page.tsx` — 루트 페이지
- `components/CameraView.tsx` — 웹캠 캡처 + canvas 오버레이 + WebSocket
