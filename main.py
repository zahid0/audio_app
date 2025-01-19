import json
import os
import secrets
import tempfile
from datetime import datetime, timedelta
from typing import List

import jwt
from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    HTTPException,
    Query,
    Request,
    status,
)
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from passlib.context import CryptContext
from starlette.middleware.sessions import SessionMiddleware

SECRET_KEY = secrets.token_hex(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

users = json.loads(os.getenv("USERS"))

app = FastAPI()


@app.middleware("http")
async def add_cache_headers(request: Request, call_next):
    response = await call_next(request)
    if os.getenv("ENV") != "dev":
        response.headers["Cache-Control"] = "public, max-age=3600"
    return response


app.add_middleware(
    SessionMiddleware,
    secret_key=secrets.token_urlsafe(32),
    max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

if os.getenv("USE_DRIVE"):
    from drive_service import DriveService

    drive_service = DriveService(os.getenv("DRIVE_TOKEN_PATH"))
else:
    from local_storage_service import LocalStorageService

    drive_service = LocalStorageService("audios")


def remove_file(path: str) -> None:
    os.remove(path)


async def authenticate_request(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    return username


# Dependency to get the current user
async def authenticate_session(request: Request):
    if "user" not in request.session:
        raise HTTPException(status_code=401, detail="Unauthenticated")
    return request.session["user"]


async def precalculate_filename_to_fileid():
    items = drive_service.list_files()
    filename_to_fileid = {item["name"]: item["id"] for item in items}
    return filename_to_fileid


folders_to_show = set([f for f in os.getenv("FOLDERS_TO_SHOW", "").split(",") if f])
filename_to_fileid = {}

folders = drive_service.list_folders()
if folders_to_show:
    folders = [f for f in folders if f["name"] in folders_to_show]
id2folder = {f["id"]: f["name"] for f in folders}
folder2id = {v: k for k, v in id2folder.items()}


@app.post("/api/token")
async def login_for_access_token(
    request: Request, form_data: OAuth2PasswordRequestForm = Depends()
):
    if not pwd_context.verify(form_data.password, users.get(form_data.username)):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = jwt.encode(
        {
            "sub": form_data.username,
            "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    request.session["user"] = form_data.username
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/collections")
async def collections(token: str = Depends(authenticate_request)):
    global folders, id2folder, folder2id, folders_to_show
    folders = drive_service.list_folders()
    if folders_to_show:
        folders = [f for f in folders if f["name"] in folders_to_show]
    id2folder = {f["id"]: f["name"] for f in folders}
    folder2id = {v: k for k, v in id2folder.items()}

    collection = [{"id": folder2id[f], "name": f} for f in folder2id.keys()]
    return JSONResponse(content=collection)


@app.get("/api/audios/{folder_id}")
async def get_audios(folder_id: str, token: str = Depends(authenticate_request)):
    if folder_id not in id2folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    items = drive_service.list_files(folder_id)

    audio_files = []
    for item in items:
        audio_files.append(
            {"id": item["id"], "title": item["name"], "url": f"/audios/{item['id']}"}
        )

    return JSONResponse(content=audio_files)


@app.get("/api/search", response_model=List[str])
async def search(query: str = Query(..., min_length=1), token: str = Depends(authenticate_request)):
    search_result = drive_service.search(query)
    filtered_result = [
        item.rsplit(".json", 1)[0] for item in search_result if item.endswith(".json")
    ]
    return filtered_result


@app.get("/audios/{file_id:path}")
async def play(
    file_id: str,
    background_tasks: BackgroundTasks,
    current_user: str = Depends(authenticate_session),
):
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file_path = temp_file.name
        drive_service.download_media(file_id, temp_file)

    background_tasks.add_task(remove_file, temp_file_path)

    return FileResponse(
        temp_file_path,
        media_type="audio/mpeg",
    )


@app.get("/api/transcripts/{file_title}")
async def get_transcript(file_title: str, token: str = Depends(authenticate_request)):
    global filename_to_fileid
    filename = f"{file_title}.json"  # Append ".json" to filename

    # If the filename is not in our dictionary, recalculate it
    if filename not in filename_to_fileid:
        filename_to_fileid = await precalculate_filename_to_fileid()

    if filename not in filename_to_fileid:
        raise HTTPException(status_code=404, detail="File not found")
    file_id = filename_to_fileid[filename]
    data_str = drive_service.get_file(file_id)
    segments = json.loads(data_str.decode("utf-8"))
    text = "\n".join([s["text"] for s in segments])
    return JSONResponse(
        content={"text": text},
    )


current_dir = os.path.dirname(__file__)
static_dir = os.path.join(current_dir, "dist")
app.mount("/", StaticFiles(directory=static_dir, html=True), name="dist")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
