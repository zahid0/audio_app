import io

from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SCOPES = [
    "https://www.googleapis.com/auth/drive.metadata.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]


class DriveService:
    def __init__(self, token_file):
        self.token_file = token_file
        self.creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        if self.creds.expired and self.creds.refresh_token:
            self.creds.refresh(GoogleRequest())
            with open(token_file, "w") as token:
                token.write(self.creds.to_json())
        self.service = build("drive", "v3", credentials=self.creds)

    def list_folders(self):
        results = (
            self.service.files()
            .list(
                q="mimeType='application/vnd.google-apps.folder'",
                fields="nextPageToken, files(id, name)",
            )
            .execute()
        )
        return results.get("files", [])

    def list_files(self, folder_id=None):
        items = []
        nextPageToken = None
        fields = "nextPageToken, files(id, name)"
        query = f"'{folder_id}' in parents" if folder_id else None
        while True:
            if query:
                results = (
                    self.service.files()
                    .list(
                        pageToken=nextPageToken,
                        q=query,
                        fields=fields,
                        orderBy="createdTime desc",
                    )
                    .execute()
                )
            else:
                results = (
                    self.service.files()
                    .list(
                        pageToken=nextPageToken,
                        fields=fields,
                        orderBy="createdTime desc",
                    )
                    .execute()
                )
            items += results.get("files", [])
            nextPageToken = results.get("nextPageToken")
            if not nextPageToken:
                break
        return items

    def get_file(self, file_id):
        return self.service.files().get_media(fileId=file_id).execute()

    def download_media(self, file_id, buffer):
        file_req = self.service.files().get_media(fileId=file_id)
        downloader = MediaIoBaseDownload(buffer, file_req)
        done = False

        while not done:
            _, done = downloader.next_chunk()

    async def media_stream(self, file_id: str):
        file_req = self.service.files().get_media(fileId=file_id)
        with io.BytesIO() as buffer:
            downloader = MediaIoBaseDownload(buffer, file_req)
            done = False
            read_position = 0

            while not done:
                buffer.seek(0, io.SEEK_END)
                _, done = downloader.next_chunk()
                buffer.seek(read_position)
                chunk = buffer.read()
                read_position = buffer.tell()
                yield chunk
