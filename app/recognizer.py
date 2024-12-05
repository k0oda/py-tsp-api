import io
import json
import wave

import librosa
import numpy as np
import vosk
from pydub import AudioSegment

model = vosk.Model(lang="ru")


def get_gender(audio_chunk: bytes) -> str:
    audio = AudioSegment.from_raw(
        io.BytesIO(audio_chunk),
        sample_width=2,
        frame_rate=16000,
        channels=1,
    )
    buffer = io.BytesIO()
    audio.export(buffer, format="wav")
    buffer.seek(0)

    y, sr = librosa.load(buffer, sr=16000)
    n_fft = min(len(y), 2048)
    chroma = librosa.feature.chroma_stft(y=y, sr=sr, n_fft=n_fft)
    return "male" if np.mean(chroma) > 0.1 else "female"


def is_high_pitch(audio_chunk: bytes) -> bool:
    threshold = 0.7
    audio_array = np.frombuffer(audio_chunk, dtype=np.int16)
    amplitude = np.max(np.abs(audio_array))
    return bool(amplitude > threshold)


def calculate_result_duration(dialog: list) -> dict:
    result_duration = {
        "receiver": 0,
        "transmitter": 0,
    }
    for item in dialog:
        if item["source"] == "receiver":
            result_duration["receiver"] += round(item["duration"], 2)
        elif item["source"] == "transmitter":
            result_duration["transmitter"] += round(item["duration"], 2)
    return result_duration


def split_by_timing(words: list) -> list:
    sentences = []
    current_sentence = []
    last_end = None

    for word in words:
        if last_end is not None and word["start"] - last_end > 0.5:
            sentences.append(" ".join(current_sentence))
            current_sentence = []

        current_sentence.append(word["word"])
        last_end = word["end"]
    if current_sentence:
        sentences.append(" ".join(current_sentence))
    return sentences


def process_result(result: dict, chunk: bytes, last_source: str) -> tuple:
    dialog = []
    words = result.get("result", [])

    if "text" in result and result["text"].strip():
        sentences = split_by_timing(words)
        for sentence in sentences:
            source = "receiver" if last_source == "transmitter" else "transmitter"
            sentence_duration = sum(
                word["end"] - word["start"] for word in words if word["word"] in sentence
            )
            dialog_item = {
                "source": source,
                "text": sentence,
                "duration": round(sentence_duration, 2),
                "gender": get_gender(chunk),
                "raised_voice": is_high_pitch(chunk),
            }
            last_source = "receiver" if last_source == "transmitter" else "transmitter"
            dialog.append(dialog_item)

    return (dialog, last_source)


def recognize(wf: wave.Wave_read) -> tuple:
    rec = vosk.KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)

    dialog = []

    last_source = "transmitter"

    last_valid_chunk = None

    while True:
        chunk = wf.readframes(500)
        if not chunk:
            break
        last_valid_chunk = chunk
        if rec.AcceptWaveform(chunk):
            result = json.loads(rec.Result())
            processed_dialog, last_source = process_result(result, chunk, last_source)
            dialog.extend(processed_dialog)

    remaining_chunk = wf.readframes(wf.getnframes() - wf.tell())
    chunk = remaining_chunk if remaining_chunk else last_valid_chunk

    final_result = json.loads(rec.FinalResult())
    processed_dialog, last_source = process_result(final_result, chunk, last_source)
    dialog.extend(processed_dialog)

    result_duration = calculate_result_duration(dialog)

    return (dialog, result_duration)
