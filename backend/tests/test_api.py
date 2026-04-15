import os

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["UPLOAD_DIR"] = "./test_uploads"

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_upload_and_summary_and_chat_flow():
    upload = client.post(
        "/api/v1/upload",
        files={"file": ("sample.mp3", b"dummy-bytes", "audio/mpeg")},
    )
    assert upload.status_code == 200
    media_id = upload.json()["media_id"]
    assert upload.json()["media_url"].endswith(f"/api/v1/media/{media_id}/file")
    media_file = client.get(f"/api/v1/media/{media_id}/file")
    assert media_file.status_code == 200

    summary = client.get(f"/api/v1/summary/{media_id}")
    assert summary.status_code == 200
    assert len(summary.json()["summary"]) > 0

    chat = client.post(
        "/api/v1/chat",
        json={"media_id": media_id, "question": "What is the file about?"},
    )
    assert chat.status_code == 200
    assert "media_url" in chat.json()

    topic = client.post(
        "/api/v1/timestamps",
        json={"media_id": media_id, "topic": "Transcription unavailable"},
    )
    assert topic.status_code == 200
    assert topic.json()["playable_url"].startswith("/api/v1/media/")


def test_not_found_media():
    response = client.get("/api/v1/summary/999999")
    assert response.status_code == 404


def test_media_file_endpoint_not_found():
    response = client.get("/api/v1/media/999999/file")
    assert response.status_code == 404


def test_chat_and_timestamps_not_found():
    chat = client.post("/api/v1/chat", json={"media_id": 999999, "question": "x"})
    assert chat.status_code == 404

    ts = client.post("/api/v1/timestamps", json={"media_id": 999999, "topic": "x"})
    assert ts.status_code == 404


def test_media_file_missing_on_disk_returns_404():
    upload = client.post(
        "/api/v1/upload",
        files={"file": ("gone.mp3", b"dummy-bytes", "audio/mpeg")},
    )
    media_id = upload.json()["media_id"]
    media_info = client.get(f"/api/v1/media/{media_id}/file")
    assert media_info.status_code == 200

    from app.core.database import SessionLocal
    from app.models.entities import MediaAsset

    db = SessionLocal()
    try:
        media = db.get(MediaAsset, media_id)
        media.file_path = "./nonexistent/removed.mp3"
        db.commit()
    finally:
        db.close()

    missing = client.get(f"/api/v1/media/{media_id}/file")
    assert missing.status_code == 404
