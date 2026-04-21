"use client";

import { useEffect, useRef, useState } from "react";

type Detection = {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  confidence: number;
};

type AnalyzeResponse = {
  frame: { width: number; height: number };
  count: number;
  people: Detection[];
  inference_ms: number;
};

const WS_URL = process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000/ws/analyze";
const ANALYZE_FPS = 4;
const JPEG_QUALITY = 0.7;

const CameraView = () => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const captureCanvasRef = useRef<HTMLCanvasElement | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const latestRef = useRef<AnalyzeResponse | null>(null);
  const inflightRef = useRef(false);

  const [status, setStatus] = useState<"idle" | "connecting" | "streaming" | "error">("idle");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [stats, setStats] = useState<{ count: number; inferenceMs: number }>({
    count: 0,
    inferenceMs: 0,
  });

  useEffect(() => {
    let stopped = false;
    let stream: MediaStream | null = null;
    let animationId = 0;
    let captureTimer: ReturnType<typeof setInterval> | null = null;

    const drawOverlay = () => {
      const canvas = canvasRef.current;
      const video = videoRef.current;
      if (!canvas || !video || video.readyState < 2) {
        animationId = requestAnimationFrame(drawOverlay);
        return;
      }
      const vw = video.videoWidth;
      const vh = video.videoHeight;
      if (canvas.width !== vw || canvas.height !== vh) {
        canvas.width = vw;
        canvas.height = vh;
      }
      const ctx = canvas.getContext("2d");
      if (!ctx) {
        animationId = requestAnimationFrame(drawOverlay);
        return;
      }
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const latest = latestRef.current;
      if (latest) {
        const sx = canvas.width / latest.frame.width;
        const sy = canvas.height / latest.frame.height;
        ctx.lineWidth = 3;
        ctx.strokeStyle = "#22d3ee";
        ctx.fillStyle = "#22d3ee";
        ctx.font = "16px ui-sans-serif, system-ui, sans-serif";
        latest.people.forEach((p, idx) => {
          const x = p.x1 * sx;
          const y = p.y1 * sy;
          const w = (p.x2 - p.x1) * sx;
          const h = (p.y2 - p.y1) * sy;
          ctx.strokeRect(x, y, w, h);
          const label = `#${idx + 1}  ${(p.confidence * 100).toFixed(0)}%`;
          const tw = ctx.measureText(label).width + 10;
          ctx.fillRect(x, Math.max(0, y - 22), tw, 22);
          ctx.fillStyle = "#0b0f14";
          ctx.fillText(label, x + 5, Math.max(14, y - 6));
          ctx.fillStyle = "#22d3ee";
        });
      }
      animationId = requestAnimationFrame(drawOverlay);
    };

    const captureAndSend = () => {
      const ws = wsRef.current;
      const video = videoRef.current;
      if (!ws || ws.readyState !== WebSocket.OPEN) return;
      if (!video || video.readyState < 2) return;
      if (inflightRef.current) return;

      if (!captureCanvasRef.current) {
        captureCanvasRef.current = document.createElement("canvas");
      }
      const capture = captureCanvasRef.current;
      capture.width = video.videoWidth;
      capture.height = video.videoHeight;
      const ctx = capture.getContext("2d");
      if (!ctx) return;
      ctx.drawImage(video, 0, 0);
      capture.toBlob(
        (blob) => {
          if (!blob || stopped) return;
          inflightRef.current = true;
          blob.arrayBuffer().then((buf) => {
            if (stopped) {
              inflightRef.current = false;
              return;
            }
            try {
              ws.send(buf);
            } catch (err) {
              console.error(err);
              inflightRef.current = false;
            }
          });
        },
        "image/jpeg",
        JPEG_QUALITY,
      );
    };

    const connect = async () => {
      setStatus("connecting");
      setErrorMsg(null);
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: { width: 1280, height: 720 },
          audio: false,
        });
      } catch (err) {
        console.error(err);
        setStatus("error");
        setErrorMsg("웹캠 권한이 거부되었거나 사용 중입니다.");
        return;
      }
      if (stopped || !videoRef.current) return;
      videoRef.current.srcObject = stream;
      await videoRef.current.play().catch(() => undefined);

      const ws = new WebSocket(WS_URL);
      ws.binaryType = "arraybuffer";
      wsRef.current = ws;

      ws.onopen = () => {
        if (stopped) return;
        setStatus("streaming");
        captureTimer = setInterval(captureAndSend, Math.round(1000 / ANALYZE_FPS));
      };
      ws.onmessage = (ev) => {
        inflightRef.current = false;
        try {
          const data = JSON.parse(ev.data) as AnalyzeResponse;
          latestRef.current = data;
          setStats({ count: data.count, inferenceMs: data.inference_ms });
        } catch (err) {
          console.error("invalid ws payload", err);
        }
      };
      ws.onerror = () => {
        setStatus("error");
        setErrorMsg("백엔드 WebSocket 연결 실패 (localhost:8000 실행 중인지 확인).");
      };
      ws.onclose = () => {
        if (!stopped) {
          setStatus("error");
          setErrorMsg("백엔드 연결이 종료되었습니다.");
        }
      };

      animationId = requestAnimationFrame(drawOverlay);
    };

    connect();

    return () => {
      stopped = true;
      if (captureTimer) clearInterval(captureTimer);
      if (animationId) cancelAnimationFrame(animationId);
      if (wsRef.current) wsRef.current.close();
      if (stream) stream.getTracks().forEach((t) => t.stop());
    };
  }, []);

  return (
    <section className="w-full max-w-4xl flex flex-col gap-3">
      <div className="relative rounded-lg overflow-hidden bg-black aspect-video">
        <video
          ref={videoRef}
          className="absolute inset-0 w-full h-full object-contain"
          muted
          playsInline
        />
        <canvas
          ref={canvasRef}
          className="absolute inset-0 w-full h-full pointer-events-none"
        />
        <div className="absolute top-2 left-2 bg-black/60 px-3 py-1 rounded text-sm">
          상태: <span className="font-medium">{status}</span>
          {errorMsg && <span className="text-red-400 ml-2">{errorMsg}</span>}
        </div>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-gray-800/60 rounded p-4">
          <div className="text-xs text-gray-400">현재 인원</div>
          <div className="text-3xl font-semibold">{stats.count}</div>
        </div>
        <div className="bg-gray-800/60 rounded p-4">
          <div className="text-xs text-gray-400">추론 시간</div>
          <div className="text-3xl font-semibold">{stats.inferenceMs.toFixed(1)} ms</div>
        </div>
      </div>
    </section>
  );
};

export default CameraView;
