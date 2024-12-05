# PY-TSP-API

This is a project, containing API for speech recognition made with FastAPI and Vosk.

## API

1. Contains `Record` models for storing processed dialogs.
2. Contains `DialogItem` model for storing each dialog phrase with `source`, `text`, `duration`, `raised_voice` and `gender` fields.
3. Implements `/asr` API endpoint for accepting audio source to be processed.

## Speech Recognition

1. Implements basic speaking source recogntion by using `last_source` variable, which changes after each phrase.
2. Calculates `duration` of phrase by calculating difference between `word end` and `word start` timings.
3. Determines `gender` using a simple librosa `chroma_stft` (chroma-based feature) and comparing it to threshold.
4. Determines `is_high_pitch` using `amplitude` comparison to `threshold`.

## Tech Stack

- Python 3.12.3
- FastAPI 0.115.6
- Vosk 0.3.45

## System Dependencies

- `ffmpeg`
- `avcodec`
- `libsndfile1`

## Installation
### Install system dependencies:
#### Ubuntu
```bash
sudo apt install ffmpeg libavcodec-extra libsndfile1
```

### Install Python dependencies:
```bash
make install
```

### Run:
```bash
make run
```

### You can find test Postman collection at project root:
`py-tsp-api.postman_collection`

### For linting use:
```bash
make lint
```
