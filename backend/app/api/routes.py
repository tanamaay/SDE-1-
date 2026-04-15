import json
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.entities import ChatLog, MediaAsset
from app.schemas.media import (
    AskRequest,
    AskResponse,
    SummaryResponse,
    TopicTimestampRequest,
    TopicTimestampResponse,
    UploadResponse,
)
from app.services.file_service import FileService
from app.services.llm_service import LLMService
from app.services.timestamp_service import TimestampService
from app.services.transcription_service import TranscriptionService
from app.services.vector_service import vector_store

router = APIRouter(prefix="/api/v1", tags=["media"])
llm_service = LLMService()
timestamp_service = TimestampService()
transcription_service = TranscriptionService()


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_path = await FileService.save_upload(file, settings.upload_dir)
    transcript, segments = transcription_service.transcribe(file_path)

    media = MediaAsset(
        filename=file.filename,
        file_path=str(file_path),
        file_type=file.content_type or "unknown",
        transcript=transcript,
        transcript_segments=json.dumps(segments),
    )
    db.add(media)
    db.commit()
    db.refresh(media)

    vector_store.upsert(media.id, transcript)

    return UploadResponse(
        media_id=media.id,
        filename=media.filename,
        file_type=media.file_type,
        media_url=f"/api/v1/media/{media.id}/file",
    )


@router.get("/summary/{media_id}", response_model=SummaryResponse)
def summarize_media(media_id: int, db: Session = Depends(get_db)):
    media = db.get(MediaAsset, media_id)
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    summary = llm_service.summarize(media.transcript or "")
    media.summary = summary
    db.commit()

    return SummaryResponse(media_id=media.id, summary=summary)


@router.post("/chat", response_model=AskResponse)
def chat_with_media(payload: AskRequest, db: Session = Depends(get_db)):
    media = db.get(MediaAsset, payload.media_id)
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    context = vector_store.retrieve(payload.media_id, payload.question)
    answer = llm_service.answer_question(context, payload.question)
    timestamps = timestamp_service.extract_from_answer(answer)
    if not timestamps:
        segments = json.loads(media.transcript_segments) if media.transcript_segments else []
        timestamps = timestamp_service.extract_topic_timestamps(media.transcript or "", payload.question, segments)

    db.add(ChatLog(media_id=payload.media_id, question=payload.question, answer=answer))
    db.commit()

    return AskResponse(answer=answer, timestamps=timestamps, media_url=f"/api/v1/media/{media.id}/file")


@router.post("/timestamps", response_model=TopicTimestampResponse)
def get_timestamps(payload: TopicTimestampRequest, db: Session = Depends(get_db)):
    media = db.get(MediaAsset, payload.media_id)
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    segments = json.loads(media.transcript_segments) if media.transcript_segments else []
    timestamps = timestamp_service.extract_topic_timestamps(media.transcript or "", payload.topic, segments)
    if not timestamps:
        timestamps = [0.0]
    playable_url = f"/api/v1/media/{media.id}/file?start={timestamps[0]}"

    return TopicTimestampResponse(topic=payload.topic, timestamps=timestamps, playable_url=playable_url)


@router.get("/media/{media_id}/file")
def get_media_file(media_id: int, db: Session = Depends(get_db)):
    media = db.get(MediaAsset, media_id)
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    media_path = Path(media.file_path)
    if not media_path.exists():
        raise HTTPException(status_code=404, detail="Media file missing on server")
    return FileResponse(path=media_path, media_type=media.file_type, filename=media.filename)
