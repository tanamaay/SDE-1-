from pydantic import BaseModel


class TranscriptSegment(BaseModel):
    start: float
    end: float
    text: str


class UploadResponse(BaseModel):
    media_id: int
    filename: str
    file_type: str
    media_url: str


class SummaryResponse(BaseModel):
    media_id: int
    summary: str


class AskRequest(BaseModel):
    media_id: int
    question: str


class AskResponse(BaseModel):
    answer: str
    timestamps: list[float]
    media_url: str


class TopicTimestampRequest(BaseModel):
    media_id: int
    topic: str


class TopicTimestampResponse(BaseModel):
    topic: str
    timestamps: list[float]
    playable_url: str
