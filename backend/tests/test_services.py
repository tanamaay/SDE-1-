from app.services.llm_service import LLMService
from app.services.timestamp_service import TimestampService
from app.services.transcription_service import TranscriptionService
from app.services.vector_service import FaissVectorStore


def test_llm_fallback_summary_and_answer():
    service = LLMService()
    assert service.summarize("") == "No content available to summarize."
    summary = service.summarize("This is a sample transcript for testing summary generation.")
    answer = service.answer_question("Context about topic", "What is topic?")
    assert summary
    assert "Answer to question" in answer


def test_llm_openai_branch_calls_internal_methods(monkeypatch):
    service = LLMService()
    service.client = object()
    monkeypatch.setattr(service, "_summarize_with_openai", lambda text: "openai summary")
    monkeypatch.setattr(service, "_answer_with_openai", lambda context, question: "openai answer 12s")

    assert service.summarize("content") == "openai summary"
    assert service.answer_question("ctx", "q") == "openai answer 12s"


def test_timestamp_service_from_answer_and_topic():
    service = TimestampService()
    assert service.extract_from_answer("Relevant points at 10.5s and 22s") == [10.5, 22.0]

    segments = [
        {"start": 4.0, "end": 8.0, "text": "introduction and setup"},
        {"start": 12.0, "end": 15.0, "text": "database topic"},
    ]
    assert service.extract_topic_timestamps("overall transcript", "database", segments) == [12.0]
    assert service.extract_topic_timestamps("overall transcript", "missing", segments) == []
    assert service.extract_topic_timestamps("this transcript has python", "python", None) == [0.0]


def test_transcription_service_fallback_for_audio_without_key(tmp_path):
    file_path = tmp_path / "sample.mp3"
    file_path.write_bytes(b"test")

    service = TranscriptionService()
    transcript, segments = service.transcribe(file_path)

    assert "Transcription unavailable" in transcript
    assert segments[0]["start"] == 0.0


def test_transcription_service_unsupported_extension(tmp_path):
    file_path = tmp_path / "notes.txt"
    file_path.write_text("hello", encoding="utf-8")

    service = TranscriptionService()
    transcript, segments = service.transcribe(file_path)

    assert "Unsupported file extension" in transcript
    assert segments


def test_vector_store_upsert_and_retrieve():
    store = FaissVectorStore()
    embedding = store._fallback_embed("fastapi vector test")
    assert embedding.shape[0] == store.DIM
    store.upsert(1, "python fastapi media upload")
    store.upsert(2, "react frontend player timestamp")

    assert "python" in store.retrieve(1, "fastapi question")
    other = store.retrieve(99, "frontend")
    assert isinstance(other, str)


def test_vector_store_retrieve_when_empty():
    store = FaissVectorStore()
    assert store.retrieve(42, "anything") == ""
