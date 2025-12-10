import asyncio

from typing import Annotated
from io import BytesIO

from fastapi import FastAPI, File, Form  # type: ignore
from fastapi.staticfiles import StaticFiles  # type: ignore
from fastapi.responses import FileResponse, StreamingResponse  # type: ignore

from yomigana_ebook.process_ebook import process_ebook


app: FastAPI = FastAPI()

app.mount("/assets", StaticFiles(directory="client/dist/assets"), "assets")


@app.get("/")
async def index() -> FileResponse:
    return FileResponse("client/dist/index.html")


@app.get("/favicon.ico")
async def get_favicon() -> FileResponse:
    return FileResponse("client/dist/favicon.ico")


@app.post("/api/process-ebook")
async def process_ebook_handler(
    ebook: Annotated[bytes, File()],
    filter: Annotated[bool, Form()] = False
) -> StreamingResponse:
    return StreamingResponse(process_ebook_streamer(ebook, filter))


async def process_ebook_streamer(ebook: bytes, filter_non_japanese: bool):
    with BytesIO(ebook) as reader, BytesIO() as writer:
        await asyncio.to_thread(process_ebook, reader, writer, filter_non_japanese)
        yield writer.getbuffer().tobytes()
