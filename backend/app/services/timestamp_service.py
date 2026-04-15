import re
from typing import Any


class TimestampService:
    def extract_topic_timestamps(
        self, transcript: str, topic: str, segments: list[dict[str, Any]] | None = None
    ) -> list[float]:
        if segments:
            topic_lower = topic.lower()
            matched = [
                float(segment.get("start", 0.0))
                for segment in segments
                if topic_lower in str(segment.get("text", "")).lower()
            ]
            if matched:
                return matched[:5]
        if topic.lower() in transcript.lower():
            return [0.0]
        return []

    def extract_from_answer(self, answer: str) -> list[float]:
        matches = re.findall(r"(\d+(?:\.\d+)?)s", answer)
        return [float(m) for m in matches] if matches else []
