from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile


class FileService:
    @staticmethod
    async def save_upload(upload_file: UploadFile, upload_dir: str) -> Path:
        Path(upload_dir).mkdir(parents=True, exist_ok=True)
        safe_name = upload_file.filename.replace(" ", "_")
        target_path = Path(upload_dir) / f"{uuid4().hex}_{safe_name}"
        content = await upload_file.read()
        target_path.write_bytes(content)
        return target_path
