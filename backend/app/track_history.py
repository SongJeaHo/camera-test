"""WebSocket 세션 단위로 track_id별 첫 등장 시각을 저장하고 체류시간을 계산."""
from __future__ import annotations

from typing import Dict, Iterable


class TrackHistory:
    """track_id → first_seen / last_seen 시각(epoch sec).

    last_seen이 ttl_sec를 초과해 갱신되지 않으면 항목을 폐기한다.
    """

    def __init__(self, ttl_sec: float = 10.0) -> None:
        self.ttl_sec = ttl_sec
        self.first_seen: Dict[int, float] = {}
        self.last_seen: Dict[int, float] = {}

    def update(self, track_ids: Iterable[int], now: float) -> None:
        seen_now = set()
        for tid in track_ids:
            if tid is None:
                continue
            self.first_seen.setdefault(tid, now)
            self.last_seen[tid] = now
            seen_now.add(tid)
        # TTL eviction
        stale = [tid for tid, ts in self.last_seen.items() if now - ts > self.ttl_sec]
        for tid in stale:
            self.first_seen.pop(tid, None)
            self.last_seen.pop(tid, None)

    def dwell(self, track_id: int, now: float) -> float:
        first = self.first_seen.get(track_id)
        if first is None:
            return 0.0
        return max(0.0, now - first)
