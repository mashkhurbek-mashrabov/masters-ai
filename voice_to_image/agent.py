import io
import logging
import base64
from openai import OpenAI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("VoiceToImageAgent")

STT_MODEL = "whisper-1"
LLM_MODEL = "gpt-4o-mini"
IMAGE_MODEL = "dall-e-3"


class VoiceToImageAgent:

    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        logger.info("Agent initialized with models: STT=%s, LLM=%s, IMAGE=%s", STT_MODEL, LLM_MODEL, IMAGE_MODEL)

    def transcribe(self, audio_bytes: bytes, filename: str = "recording.wav") -> str:
        logger.info("Step 1/3 — Transcribing audio (%d bytes) with %s ...", len(audio_bytes), STT_MODEL)
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = filename
        transcript = self.client.audio.transcriptions.create(
            model=STT_MODEL,
            file=audio_file,
        )
        text = transcript.text
        logger.info("Transcription result: %s", text)
        return text

    def generate_image_prompt(self, transcript: str) -> str:
        logger.info("Step 2/3 — Generating image prompt with %s ...", LLM_MODEL)
        system_msg = (
            "You are a creative assistant that converts user requests into detailed, "
            "vivid image-generation prompts suitable for DALL-E. "
            "Return ONLY the image prompt, nothing else. "
            "Make the prompt descriptive with style, lighting, composition, and mood details."
        )
        response = self.client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": transcript},
            ],
            temperature=0.7,
            max_tokens=300,
        )
        prompt = response.choices[0].message.content.strip()
        logger.info("Generated image prompt: %s", prompt)
        return prompt

    def generate_image(self, prompt: str) -> str:
        logger.info("Step 3/3 — Generating image with %s ...", IMAGE_MODEL)
        response = self.client.images.generate(
            model=IMAGE_MODEL,
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            response_format="b64_json",
            n=1,
        )
        image_b64 = response.data[0].b64_json
        logger.info("Image generated successfully (%d base64 chars)", len(image_b64))
        return image_b64

    def run(self, audio_bytes: bytes) -> dict:
        logger.info("=" * 60)
        logger.info("PIPELINE START")
        logger.info("=" * 60)

        transcript = self.transcribe(audio_bytes)
        image_prompt = self.generate_image_prompt(transcript)
        image_b64 = self.generate_image(image_prompt)

        logger.info("=" * 60)
        logger.info("PIPELINE COMPLETE")
        logger.info("=" * 60)

        return {
            "transcript": transcript,
            "image_prompt": image_prompt,
            "image_b64": image_b64,
            "models": {
                "stt": STT_MODEL,
                "llm": LLM_MODEL,
                "image": IMAGE_MODEL,
            },
        }
