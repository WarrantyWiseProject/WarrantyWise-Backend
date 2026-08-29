import io, json, re
from fastapi import UploadFile
from app.core.config import settings

def _folder_id() -> str | None:
    link = settings.google_drive_folder_link or ""
    match = re.search(r"folders/([a-zA-Z0-9_-]+)", link)
    return match.group(1) if match else (link or None)

async def upload_photo(file: UploadFile) -> str:
    if not settings.google_drive_credentials_json and not settings.google_drive_credentials_file:
        raise RuntimeError("Google Drive credentials are not configured")
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload
    scopes = ["https://www.googleapis.com/auth/drive.file"]
    if settings.google_drive_credentials_json:
        credentials = service_account.Credentials.from_service_account_info(json.loads(settings.google_drive_credentials_json.get_secret_value()), scopes=scopes)
    else:
        credentials = service_account.Credentials.from_service_account_file(settings.google_drive_credentials_file, scopes=scopes)
    content = await file.read()
    service = build("drive", "v3", credentials=credentials, cache_discovery=False)
    folder_id = _folder_id()
    metadata = {"name": file.filename or "warrantywise-photo"}
    if folder_id:
        metadata["parents"] = [folder_id]
    uploaded = service.files().create(body=metadata, media_body=MediaIoBaseUpload(io.BytesIO(content), mimetype=file.content_type or "application/octet-stream"), fields="id").execute()
    service.permissions().create(fileId=uploaded["id"], body={"type": "anyone", "role": "reader"}).execute()
    return f"https://drive.google.com/uc?id={uploaded['id']}"
