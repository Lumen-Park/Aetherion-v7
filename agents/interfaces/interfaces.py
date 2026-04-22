"""
Hardware Interfaces – Voice, Vision, Email, Scheduler.
"""

import os
import smtplib
import threading
import time
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Callable, List, Optional

# Optional imports with graceful fallback
try:
    import pyttsx3
    import speech_recognition as sr

    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False

try:
    import pyautogui
    from PIL import ImageGrab

    VISION_AVAILABLE = True
except ImportError:
    VISION_AVAILABLE = False

try:
    import schedule

    SCHEDULER_AVAILABLE = True
except ImportError:
    SCHEDULER_AVAILABLE = False

from core.protocol import LLMWrapper


class VoiceInterface:
    def __init__(self, offline: bool = False):
        if not VOICE_AVAILABLE:
            raise ImportError("Voice dependencies missing.")
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.llm = LLMWrapper()
        self.offline = offline

    def listen(self) -> str:
        with sr.Microphone() as source:
            print("🎤 Listening...")
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source)
        try:
            if self.offline:
                try:
                    text = self.recognizer.recognize_sphinx(audio)
                except Exception:
                    text = self.recognizer.recognize_google(audio)
            else:
                text = self.recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            return ""

    def speak(self, text: str):
        print(f"🔊 Speaking: {text[:100]}...")
        self.engine.say(text)
        self.engine.runAndWait()

    def chat_loop(self, callback: Callable[[str], str]):
        while True:
            user_input = self.listen()
            if user_input.lower() in ["exit", "quit", "goodbye"]:
                self.speak("Goodbye.")
                break
            if user_input:
                response = callback(user_input)
                self.speak(response)


class VisionInterface:
    def __init__(self, model: str = "llava"):
        if not VISION_AVAILABLE:
            raise ImportError("Vision dependencies missing.")
        self.model = model
        self.llm = LLMWrapper(model=model)

    def capture_screenshot(self) -> str:
        screenshot = pyautogui.screenshot()
        path = f"/tmp/screenshot_{int(time.time())}.png"
        screenshot.save(path)
        return path

    def analyze_image(
        self, image_path: str, question: str = "Describe this image."
    ) -> str:
        with open(image_path, "rb") as f:
            import base64

            image_b64 = base64.b64encode(f.read()).decode()
        prompt = f"[Image: {image_b64[:100]}...] {question}"
        response = self.llm.generate(prompt)
        return response["content"]


class EmailSender:
    def __init__(self):
        self.smtp_config = {}

    def configure(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        from_email: str,
    ):
        self.smtp_config = {
            "host": host,
            "port": port,
            "username": username,
            "password": password,
            "from_email": from_email,
        }

    def send_report(
        self,
        to_email: str,
        subject: str,
        body: str,
        attachments: List[str] = None,
    ):
        if not self.smtp_config:
            raise ValueError("Email not configured.")
        host = self.smtp_config.get("host", "")
        password = self.smtp_config.get("password", "")
        if host not in ("localhost", "127.0.0.1") and password:
            from utils.logger import AetherionLogger

            logger = AetherionLogger()
            logger.warning(
                "Sending email with plaintext password to remote SMTP server. "
                "Consider using a secret manager."
            )

        msg = MIMEMultipart()
        msg["From"] = self.smtp_config["from_email"]
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        if attachments:
            for file_path in attachments:
                with open(file_path, "rb") as f:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f'attachment; filename="{os.path.basename(file_path)}"',
                    )
                    msg.attach(part)

        with smtplib.SMTP(
            self.smtp_config["host"], self.smtp_config["port"]
        ) as server:
            server.starttls()
            server.login(
                self.smtp_config["username"], self.smtp_config["password"]
            )
            server.send_message(msg)


class CronScheduler:
    def __init__(self):
        if not SCHEDULER_AVAILABLE:
            raise ImportError("Scheduler missing.")
        self.jobs = []

    def add_daily_job(self, time_str: str, func: Callable, *args):
        schedule.every().day.at(time_str).do(func, *args)

    def add_hourly_job(self, func: Callable, *args):
        schedule.every().hour.do(func, *args)

    def start(self):
        def run_loop():
            while True:
                schedule.run_pending()
                time.sleep(1)

        thread = threading.Thread(target=run_loop, daemon=True)
        thread.start()
