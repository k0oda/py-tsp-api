from pathlib import Path

from fastapi import HTTPException
from httpx import AsyncClient, RequestError
from pydub import AudioSegment


def convert_to_wav(file_path: Path) -> Path:
    if file_path.suffix.lower() not in [".mp3", ".ogg", ".flac", ".wav"]:
        raise HTTPException(status_code=400, detail="Unsupported file format")
    if file_path.suffix.lower() != ".wav":
        audio = AudioSegment.from_file(file_path)
        audio = audio.set_frame_rate(16000).set_sample_width(2).set_channels(1)

        wav_file_path = file_path.with_suffix(".wav")

        audio.export(wav_file_path, format="wav")
        return wav_file_path
    return file_path


async def fetch_file(audio_source: str) -> Path:  # noqa: C901
    async with AsyncClient() as client:
        try:
            response = await client.get(audio_source)
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="File not found")
            elif response.status_code != 200:
                raise HTTPException(status_code=500, detail="Failed to download file")

            file_name = Path(audio_source).name
            file_path = Path(f"uploads/{file_name}")
            Path.mkdir(Path("uploads"), exist_ok=True)
            with Path.open(file_path, "wb") as f:
                f.write(response.content)
        except RequestError as e:
            raise HTTPException(status_code=400, detail=f"Invalid URL or download error: {str(e)}") from e
        else:
            return file_path


async def process_source(audio_source: str) -> str:  # noqa: C901
    if isinstance(audio_source, str):
        if audio_source.startswith(("http://", "https://")):
            file_path = await fetch_file(audio_source)
        else:
            file_path = Path(audio_source)
    else:
        raise HTTPException(status_code=400, detail="Invalid file path or URL.")

    if not file_path or not Path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found.")

    try:
        file_path = convert_to_wav(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to convert to wav.") from e

    return(file_path.as_posix())
