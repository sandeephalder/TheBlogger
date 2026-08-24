import sys
import os
import base64
import io
import wave
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from tools.sarvam_speech import SarvamSpeech
from utils.constants import (
    SARVAM_STT_TRANSLATE_MODEL_SAARAS,
    SARVAM_STT_MODEL_SAARAS_V4,
    SARVAM_TTS_MODEL_BULBUL_V3,
    SARVAM_LANGUAGE_ENGLISH,
)

def make_wav_bytes(frames: int = 800) -> bytes:
    """A tiny but structurally valid mono 16-bit WAV, as Bulbul would return."""
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(22050)
        w.writeframes(b"\x00\x01" * frames)
    return buffer.getvalue()

def make_speech(monkeypatch_env=True, **kwargs):
    with patch("tools.sarvam_speech.SarvamAI") as mock_client_cls:
        speech = SarvamSpeech(api_key="test-key", **kwargs)
        speech.client = mock_client_cls.return_value
    return speech


def test_missing_api_key_is_rejected():
    """No key means a clear error rather than a confusing SDK failure."""
    with patch("tools.sarvam_speech.os.getenv", return_value=None):
        with pytest.raises(ValueError, match="Sarvam api key not found"):
            SarvamSpeech()


def test_speech_to_english_text_uses_saaras_translate(tmp_path):
    """Voice to English text goes through translate, not transcribe."""
    audio_file = tmp_path / "input.wav"
    audio_file.write_bytes(make_wav_bytes())

    speech = make_speech()
    speech.client.speech_to_text.translate.return_value = MagicMock(transcript="What is the capital of India?")

    transcript = speech.speech_to_english_text(str(audio_file))

    assert transcript == "What is the capital of India?"
    kwargs = speech.client.speech_to_text.translate.call_args.kwargs
    assert kwargs["model"] == SARVAM_STT_TRANSLATE_MODEL_SAARAS
    speech.client.speech_to_text.transcribe.assert_not_called()


def test_speech_to_text_keeps_spoken_language(tmp_path):
    """Transcribe mode keeps the original language and auto-detects it."""
    audio_file = tmp_path / "input.wav"
    audio_file.write_bytes(make_wav_bytes())

    speech = make_speech()
    speech.client.speech_to_text.transcribe.return_value = MagicMock(transcript="भारत की राजधानी क्या है?")

    transcript = speech.speech_to_text(str(audio_file))

    assert transcript == "भारत की राजधानी क्या है?"
    kwargs = speech.client.speech_to_text.transcribe.call_args.kwargs
    assert kwargs["model"] == SARVAM_STT_MODEL_SAARAS_V4
    assert kwargs["language_code"] == "unknown"


def test_text_to_speech_writes_decoded_audio(tmp_path):
    """The base64 payload Bulbul returns is decoded onto disk as a WAV."""
    wav_bytes = make_wav_bytes()

    speech = make_speech()
    speech.client.text_to_speech.convert.return_value = MagicMock(
        audios=[base64.b64encode(wav_bytes).decode("utf-8")]
    )

    out_path = tmp_path / "nested" / "reply.wav"
    result = speech.text_to_speech("नमस्ते", str(out_path), language_code=SARVAM_LANGUAGE_ENGLISH)

    assert result == str(out_path)
    assert out_path.read_bytes() == wav_bytes
    kwargs = speech.client.text_to_speech.convert.call_args.kwargs
    assert kwargs["model"] == SARVAM_TTS_MODEL_BULBUL_V3
    assert kwargs["language_code"] == SARVAM_LANGUAGE_ENGLISH


def test_text_to_speech_rejects_empty_text(tmp_path):
    speech = make_speech()
    with pytest.raises(ValueError, match="empty text"):
        speech.text_to_speech("   ", str(tmp_path / "out.wav"))


def test_long_text_is_chunked_under_the_limit():
    """Bulbul caps each request, so long replies are split on sentences."""
    speech = make_speech(max_chars=50)
    text = " ".join(f"यह वाक्य संख्या {i} है।" for i in range(20))

    chunks = speech._chunk_text(text)

    assert len(chunks) > 1
    assert all(len(chunk) <= 50 for chunk in chunks)
    # every sentence survives the split
    assert "".join(chunks).count("।") == text.count("।")


def test_oversized_single_sentence_is_hard_cut():
    """A sentence with no boundary to split on is still kept under the limit."""
    speech = make_speech(max_chars=20)
    chunks = speech._chunk_text("क" * 95)

    assert all(len(chunk) <= 20 for chunk in chunks)
    assert "".join(chunks) == "क" * 95


def test_chunked_audio_is_stitched_into_one_wav(tmp_path):
    """Multiple Bulbul responses become a single playable file, not concatenated headers."""
    wav_bytes = make_wav_bytes(frames=800)

    speech = make_speech(max_chars=30)
    speech.client.text_to_speech.convert.return_value = MagicMock(
        audios=[base64.b64encode(wav_bytes).decode("utf-8")]
    )

    text = " ".join(f"यह वाक्य संख्या {i} है।" for i in range(6))
    out_path = tmp_path / "reply.wav"
    speech.text_to_speech(text, str(out_path))

    call_count = speech.client.text_to_speech.convert.call_count
    assert call_count > 1

    with wave.open(str(out_path), "rb") as w:
        assert w.getnchannels() == 1
        assert w.getsampwidth() == 2
        assert w.getframerate() == 22050
        assert w.getnframes() == 800 * call_count
