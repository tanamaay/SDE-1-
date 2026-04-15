from pathlib import Path
from typing import Any

from openai import OpenAI
import fitz
from pypdf import PdfReader

from app.core.config import settings


class TranscriptionService:
    PDF_EXTENSIONS = {".pdf"}
    AUDIO_VIDEO_EXTENSIONS = {
        ".mp3",
        ".wav",
        ".m4a",
        ".aac",
        ".ogg",
        ".mp4",
        ".mov",
        ".mkv",
        ".webm",
    }

    def __init__(self) -> None:
        self.client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    def transcribe(self, file_path: Path) -> tuple[str, list[dict[str, Any]]]:
        extension = file_path.suffix.lower()
        if extension in self.PDF_EXTENSIONS:
            return self._transcribe_pdf(file_path)
        if extension in self.AUDIO_VIDEO_EXTENSIONS:
            return self._transcribe_media(file_path)
        text = f"Unsupported file extension '{extension}'. File uploaded successfully."
        return text, [{"start": 0.0, "end": 0.0, "text": text}]

    def _transcribe_pdf(self, file_path: Path) -> tuple[str, list[dict[str, Any]]]:  # pragma: no cover
        reader = PdfReader(str(file_path))
        pages: list[str] = []
        for page in reader.pages:
            pages.append((page.extract_text() or "").strip())
        transcript = "\n".join(filter(None, pages)).strip()

        # Fallback parser for PDFs where pypdf fails to extract embedded text.
        if not transcript:
            with fitz.open(str(file_path)) as doc:
                fitz_pages = [(page.get_text("text") or "").strip() for page in doc]
            transcript = "\n".join(filter(None, fitz_pages)).strip()

        if not transcript:
            transcript = (
                "No readable text found in PDF. The file may be scanned/image-based and requires OCR."
            )
        return transcript, [{"start": 0.0, "end": 0.0, "text": transcript}]

    def _transcribe_media(self, file_path: Path) -> tuple[str, list[dict[str, Any]]]:  # pragma: no cover
        if not self.client:
            fallback = f"Transcription unavailable (missing OPENAI_API_KEY) for {file_path.name}."
            return fallback, [{"start": 0.0, "end": 0.0, "text": fallback}]

        with file_path.open("rb") as media_file:
            transcription = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=media_file,
                response_format="verbose_json",
            )

        transcript = (getattr(transcription, "text", None) or "").strip()
        raw_segments = getattr(transcription, "segments", []) or []
        segments: list[dict[str, Any]] = []
        for segment in raw_segments:
            start = float(getattr(segment, "start", 0.0))
            end = float(getattr(segment, "end", 0.0))
            text = (getattr(segment, "text", "") or "").strip()
            if text:
                segments.append({"start": start, "end": end, "text": text})

        if not segments:
            segments = [{"start": 0.0, "end": 0.0, "text": transcript or "No speech detected."}]
        if not transcript:
            transcript = " ".join(seg["text"] for seg in segments).strip()

        return transcript, segments
