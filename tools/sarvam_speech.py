import base64
import io
import os
import re
import sys
import wave

from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from sarvamai import SarvamAI

from utils.constants import (
    SARVAM_API_KEY,
    SARVAM_TTS_MODEL_BULBUL_V3,
    SARVAM_STT_MODEL_SAARAS_V4,
    SARVAM_STT_TRANSLATE_MODEL_SAARAS,
    SARVAM_TTS_SPEAKER_DEFAULT,
    SARVAM_TTS_MAX_CHARS,
    SARVAM_LANGUAGE_HINDI,
    SARVAM_STT_LANGUAGE_AUTO,
)
from utils.colors import print_cyan, print_green, print_yellow

load_dotenv()

# Split on sentence enders, including the Devanagari danda.
SENTENCE_SPLIT_PATTERN = r"(?<=[।.!?\n])\s*"

class SarvamSpeech:
    """
    Speech in and speech out via Sarvam.

    Saaras handles speech to text (it can transcribe in the spoken language or
    translate straight to English), and Bulbul handles text to speech.
    """

    def __init__(self, api_key=None, tts_model=SARVAM_TTS_MODEL_BULBUL_V3,
                 stt_model=SARVAM_STT_MODEL_SAARAS_V4,
                 stt_translate_model=SARVAM_STT_TRANSLATE_MODEL_SAARAS,
                 max_chars=SARVAM_TTS_MAX_CHARS):
        print("Trying to set sarvam api key")
        self.sarvam_api_key = api_key or os.getenv(SARVAM_API_KEY)
        if not self.sarvam_api_key:
            raise ValueError("Sarvam api key not found")
        self.client = SarvamAI(api_subscription_key=self.sarvam_api_key)
        self.tts_model = tts_model
        self.stt_model = stt_model
        self.stt_translate_model = stt_translate_model
        self.max_chars = max_chars

    def speech_to_english_text(self, audio_path: str) -> str:
        """
        Transcribe an audio file straight to English, whatever language was
        spoken. Saaras detects the language and translates in one call.
        """
        print_cyan(f"\n🎤 Sarvam Speech To English Text\n ===============> \nFile: {audio_path}")
        try:
            with open(audio_path, "rb") as audio_file:
                response = self.client.speech_to_text.translate(
                    file=audio_file,
                    model=self.stt_translate_model,
                )
            print_green(f"\n📝 Transcript (English):\n ===============> \n{response.transcript}")
            return response.transcript
        except Exception as e:
            raise ValueError(f"Error occurred with exception : {e}")

    def speech_to_text(self, audio_path: str, language_code: str = SARVAM_STT_LANGUAGE_AUTO) -> str:
        """
        Transcribe an audio file in the language that was spoken, without
        translating. Leave `language_code` as "unknown" to auto-detect.
        """
        print_cyan(f"\n🎤 Sarvam Speech To Text\n ===============> \nFile: {audio_path} | Language: {language_code}")
        try:
            with open(audio_path, "rb") as audio_file:
                response = self.client.speech_to_text.transcribe(
                    file=audio_file,
                    model=self.stt_model,
                    language_code=language_code,
                )
            print_green(f"\n📝 Transcript:\n ===============> \n{response.transcript}")
            return response.transcript
        except Exception as e:
            raise ValueError(f"Error occurred with exception : {e}")

    def text_to_speech(self, text: str, out_path: str,
                       language_code: str = SARVAM_LANGUAGE_HINDI,
                       speaker: str = SARVAM_TTS_SPEAKER_DEFAULT,
                       pace: float = 1.0) -> str:
        """
        Speak `text` into a WAV file at `out_path` and return that path.

        Bulbul caps each request, so long replies are split on sentence
        boundaries and the returned audio is stitched back into one file.
        """
        if not text or not text.strip():
            raise ValueError("Cannot synthesise empty text")

        chunks = self._chunk_text(text)
        print_cyan(f"\n🔊 Sarvam Text To Speech\n ===============> \nLanguage: {language_code} | Speaker: {speaker} | Chunks: {len(chunks)}")

        try:
            audio_parts = []
            for chunk in chunks:
                response = self.client.text_to_speech.convert(
                    text=chunk,
                    language_code=language_code,
                    speaker=speaker,
                    model=self.tts_model,
                    pace=pace,
                )
                audio_parts.extend(base64.b64decode(audio) for audio in response.audios)

            self._write_wav(audio_parts, out_path)
            print_green(f"\n🎧 Audio written\n ===============> \n{out_path}")
            return out_path
        except Exception as e:
            raise ValueError(f"Error occurred with exception : {e}")

    def _chunk_text(self, text: str):
        """Pack whole sentences into chunks that stay under the Bulbul limit."""
        text = text.strip()
        if len(text) <= self.max_chars:
            return [text]

        chunks = []
        current = []
        current_len = 0

        for sentence in re.split(SENTENCE_SPLIT_PATTERN, text):
            sentence = sentence.strip()
            if not sentence:
                continue

            # A single sentence longer than the limit has to be cut hard.
            while len(sentence) > self.max_chars:
                if current:
                    chunks.append(" ".join(current))
                    current, current_len = [], 0
                chunks.append(sentence[:self.max_chars])
                sentence = sentence[self.max_chars:].strip()

            separator_len = 1 if current else 0
            if current_len + separator_len + len(sentence) > self.max_chars:
                chunks.append(" ".join(current))
                current, current_len = [], 0
                separator_len = 0

            current.append(sentence)
            current_len += separator_len + len(sentence)

        if current:
            chunks.append(" ".join(current))

        return chunks

    def _write_wav(self, audio_parts, out_path: str) -> str:
        """
        Write one WAV file. WAV bytes cannot simply be concatenated — each part
        carries its own header — so the frames are copied into a single file.
        """
        directory = os.path.dirname(out_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        if len(audio_parts) == 1:
            with open(out_path, "wb") as f:
                f.write(audio_parts[0])
            return out_path

        with wave.open(out_path, "wb") as output_wav:
            params_written = False
            for part in audio_parts:
                with wave.open(io.BytesIO(part), "rb") as part_wav:
                    if not params_written:
                        output_wav.setparams(part_wav.getparams())
                        params_written = True
                    output_wav.writeframes(part_wav.readframes(part_wav.getnframes()))

        return out_path

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Sarvam speech helper")
    parser.add_argument("--speak", type=str, help="Text to synthesise")
    parser.add_argument("--listen", type=str, help="Audio file to transcribe to English")
    parser.add_argument("--out", type=str, default="sarvam_output.wav", help="Where to write synthesised audio")
    parser.add_argument("--language", type=str, default=SARVAM_LANGUAGE_HINDI, help="TTS language code")
    args = parser.parse_args()

    try:
        speech = SarvamSpeech()
        if args.listen:
            speech.speech_to_english_text(args.listen)
        if args.speak:
            speech.text_to_speech(args.speak, args.out, language_code=args.language)
        if not args.listen and not args.speak:
            print_yellow("Nothing to do — pass --speak or --listen.")
    except Exception as e:
        print(f"Connection Error: {e}")
