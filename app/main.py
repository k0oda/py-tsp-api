import wave

from fastapi import FastAPI, HTTPException

from .db import SessionDependency, init_db
from .models import DialogItem, DialogItemPublic, Record, RecordPublic, RecordRequest, RecordResultDuration
from .recognizer import recognize
from .utils import process_source

app = FastAPI()

@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/ping")
async def ping() -> dict:
    return {"ping": "pong"}

@app.post("/asr", response_model=RecordPublic)
async def asr(request: RecordRequest, session: SessionDependency) -> dict:
    file_path = await process_source(request.audio_source)

    try:
        with wave.open(file_path, "rb") as wf:
            results, result_duration = recognize(wf)

            dialog = [DialogItem(**result) for result in results]
            session.add_all(dialog)
            result_duration = RecordResultDuration(**result_duration)
            record = Record(audio_path=file_path, result_duration=result_duration, dialog=dialog)
            session.add(record)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during speech recognition: {str(e)}") from e
    else:
        session.commit()
        dialog_public = [DialogItemPublic(**result) for result in results]
        return RecordPublic(dialog=dialog_public, result_duration=result_duration)
