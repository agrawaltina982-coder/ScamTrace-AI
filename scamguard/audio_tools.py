from functools import lru_cache
from typing import Dict, Optional

LANGUAGE_MAP = {
    "Auto detect": None,
    "Hindi": "hi",
    "Marathi": "mr",
    "Bengali": "bn",
    "Gujarati": "gu",
    "Tamil": "ta",
    "Telugu": "te",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Punjabi": "pa",
    "Urdu": "ur",
    "Odia": "or",
    "Assamese": "as",
    "English": "en",
}

@lru_cache(maxsize=2)
def _load_model(model_size: str):
    from faster_whisper import WhisperModel
    return WhisperModel(model_size, device="cpu", compute_type="int8")


def transcribe_audio(audio_bytes: bytes, filename: str, language: Optional[str] = None, model_size: str = "base") -> Dict:
    """Transcribe uploaded audio locally using faster-whisper.

    The model is multilingual and can transcribe supported Indian languages.
    Audio is written to a temporary file and removed after transcription.
    """
    import os
    import tempfile

    if not audio_bytes:
        return {"available": False, "text": "", "language": None, "segments": [], "error": "Empty audio file."}

    suffix = os.path.splitext(filename or "audio.wav")[1] or ".wav"
    path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(audio_bytes)
            path = tmp.name

        model = _load_model(model_size)
        segments, info = model.transcribe(
            path,
            language=language or None,
            beam_size=5,
            vad_filter=True,
        )

        rows = []
        text_parts = []
        for seg in segments:
            piece = seg.text.strip()
            if piece:
                text_parts.append(piece)
                rows.append({"start": round(seg.start, 2), "end": round(seg.end, 2), "text": piece})

        detected = getattr(info, "language", None)
        return {
            "available": True,
            "text": " ".join(text_parts).strip(),
            "language": detected,
            "language_probability": round(float(getattr(info, "language_probability", 0.0)), 3),
            "segments": rows,
            "error": None,
            "model": model_size,
        }
    except Exception as e:
        return {
            "available": False,
            "text": "",
            "language": None,
            "segments": [],
            "error": f"Audio transcription failed: {type(e).__name__}: {e}",
            "model": model_size,
        }
    finally:
        if path:
            try:
                os.remove(path)
            except OSError:
                pass
