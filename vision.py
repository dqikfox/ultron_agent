import asyncio
import base64
import io
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import pytesseract
import requests
from PIL import ImageGrab, Image

try:
    import mss
except ImportError:
    mss = None  # pragma: no cover

from utils.ultron_logger import (
    log_ai_decision,
    log_error,
    log_file_operation,
    log_info,
)


class Vision:
    """Legacy screenshot capture and OCR helper."""

    def __init__(self) -> None:
        self.component = "vision_ocr"
        self.screenshots_dir = Path("screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)

        self.tesseract_available = self._check_tesseract()
        if self.tesseract_available:
            log_info(self.component, "Vision OCR ready")
        else:
            log_error(
                self.component,
                "Tesseract not detected; OCR features disabled",
            )

    def _check_tesseract(self) -> bool:
        """Check if the Tesseract OCR engine can be located."""

        try:
            tesseract_dir = Path(r"C:\Program Files\Tesseract-OCR")
            binary_path = tesseract_dir / "tesseract.exe"
            if binary_path.exists():
                current_path = os.environ.get("PATH", "")
                if str(tesseract_dir) not in current_path:
                    os.environ["PATH"] = f"{tesseract_dir};{current_path}"
                    log_info(
                        self.component,
                        f"Added Tesseract to PATH at {tesseract_dir}",
                    )

            possible_paths = [
                "tesseract",
                str(binary_path),
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            ]

            for candidate in possible_paths:
                try:
                    setattr(pytesseract, "tesseract_cmd", candidate)
                    pytesseract.get_tesseract_version()
                    log_info(
                        self.component,
                        f"Tesseract detected at {candidate}",
                    )
                    return True
                except Exception:
                    continue

            explicit_path = Path(
                r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            )
            try:
                setattr(pytesseract, "tesseract_cmd", str(explicit_path))
                pytesseract.get_tesseract_version()
                log_info(
                    self.component,
                    "Tesseract detected via explicit path",
                )
                return True
            except Exception:
                return False
        except Exception as exc:
            log_error(self.component, f"Tesseract detection failed: {exc}")
            return False

    def capture_screen(self) -> tuple[Image.Image, str]:
        """Capture the active screen and persist it to disk."""

        log_info(self.component, "Capturing full screen")
        screen = ImageGrab.grab()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = self.screenshots_dir / f"screenshot_{timestamp}.png"
        screen.save(filepath)
        log_file_operation(
            self.component,
            "Saved screenshot",
            str(filepath),
            "create",
        )

        return screen, str(filepath)

    def perform_ocr(self, image: Image.Image) -> str:
        """Run OCR over the provided image."""

        if not self.tesseract_available:
            log_error(
                self.component,
                "OCR requested but Tesseract is unavailable",
            )
            return (
                "OCR not available. Install Tesseract from "
                "https://github.com/UB-Mannheim/tesseract/wiki"
            )

        log_info(self.component, "Running OCR on captured image")
        try:
            text = pytesseract.image_to_string(image)
            if len(text.strip()) < 50:
                log_info(
                    self.component,
                    "Initial OCR output minimal; retrying with grayscale",
                )
                gray_image = image.convert("L")
                for config in ("--psm 3", "--psm 6", "--psm 11"):
                    try:
                        enhanced_text = pytesseract.image_to_string(
                            gray_image,
                            config=config,
                        )
                        if len(enhanced_text.strip()) > len(text.strip()):
                            text = enhanced_text
                            log_info(
                                self.component,
                                f"OCR improved with config {config}",
                            )
                            break
                    except Exception as exc:
                        log_error(
                            self.component,
                            f"OCR config {config} failed: {exc}",
                        )

            words = [word for word in text.split() if word.strip()]
            if words:
                log_info(
                    self.component,
                    f"OCR completed with {len(words)} detected words",
                )
            else:
                log_error(
                    self.component,
                    "OCR completed with no detected text",
                )
            return text
        except Exception as exc:
            log_error(self.component, f"OCR failed: {exc}")
            return f"OCR failed: {exc}"

    def capture_and_ocr(self) -> Dict[str, Any]:
        """Capture the screen and perform OCR in a single step."""

        screen, filepath = self.capture_screen()
        text = self.perform_ocr(screen)

        words = [word for word in text.split() if word.strip()]
        result = {
            "text": text,
            "screenshot_path": filepath,
            "word_count": len(words),
            "char_count": len(text.strip()),
            "has_text": bool(words),
        }

        log_info(
            self.component,
            "OCR summary",
            word_count=len(words),
            char_count=len(text.strip()),
            screenshot_path=filepath,
        )

        return result


class ScreenVisionService:
    """Real-time screen capture service with Ollama vision integration."""

    DEFAULT_PROMPT = (
        "You are assisting with live screen comprehension. "
        "Describe the current screen in detail, list key UI elements, "
        "visible text, and actionable items. Highlight anything that may "
        "require attention."
    )

    def __init__(
        self,
        model: str = "qwen2.5vl",
        ollama_url: str = "http://127.0.0.1:11434/api/chat",
        capture_interval: float = 5.0,
        request_timeout: float = 60.0,
        save_directory: Optional[str] = None,
    ) -> None:
        self.component = "screen_vision_service"
        if mss is None:
            message = (
                "ScreenVisionService requires the 'mss' package for realtime "
                "screen capture. Install it with `pip install mss`."
            )
            log_error(self.component, message)
            raise RuntimeError(message)

        self.model = model
        self.ollama_url = ollama_url
        self.request_timeout = request_timeout
        self.capture_interval = capture_interval
        if save_directory:
            self.save_directory = Path(save_directory)
        else:
            self.save_directory = Path("screenshots") / "live"
        self.save_directory.mkdir(parents=True, exist_ok=True)

        self._monitor_task: Optional[asyncio.Task] = None
        self._stop_event: Optional[asyncio.Event] = None

        log_info(
            self.component,
            "ScreenVisionService initialized",
            model=model,
            interval=capture_interval,
            ollama_url=ollama_url,
            save_directory=str(self.save_directory),
        )

    @property
    def is_running(self) -> bool:
        return self._monitor_task is not None and not self._monitor_task.done()

    def analyze_current_screen(
        self,
        prompt: Optional[str] = None,
        monitor: int = 1,
        save_image: bool = True,
    ) -> Dict[str, Any]:
        """Capture the current screen, query Ollama, and return analysis."""

        prompt_text = prompt.strip() if prompt else self.DEFAULT_PROMPT
        capture = self._capture_frame(monitor=monitor, save_image=save_image)
        image = capture["image"]
        encoded_image = self._encode_image(image)
        analysis = self._query_ollama(prompt_text, encoded_image)

        result = {
            "analysis": (analysis or "").strip(),
            "image_path": capture.get("path"),
            "captured_at": datetime.utcnow().isoformat(),
            "model": self.model,
        }

        if analysis:
            log_ai_decision(
                self.component,
                "Screen analysis completed",
                ai_model=self.model,
                captured_at=result["captured_at"],
                image_path=result.get("image_path"),
            )
        else:
            log_error(
                self.component,
                "Ollama returned no analysis for captured screen",
            )

        return result

    def monitor_screen(
        self,
        prompt: Optional[str] = None,
        duration: float = 15.0,
        interval: Optional[float] = None,
        monitor: int = 1,
        save_images: bool = False,
    ) -> Dict[str, Any]:
        """Capture and analyze the screen over a fixed duration."""

        interval_value = interval or self.capture_interval
        iterations = max(1, int(duration / interval_value))
        prompt_text = prompt.strip() if prompt else self.DEFAULT_PROMPT

        log_info(
            self.component,
            "Starting synchronous screen monitoring",
            duration=duration,
            interval=interval_value,
            monitor=monitor,
        )

        frames: List[Dict[str, Any]] = []
        start_time = time.monotonic()
        for index in range(iterations):
            frame_result = self.analyze_current_screen(
                prompt_text, monitor=monitor, save_image=save_images
            )
            frame_result["iteration"] = index + 1
            frames.append(frame_result)

            # Avoid sleeping after the last frame
            if index < iterations - 1:
                time.sleep(interval_value)

        elapsed = time.monotonic() - start_time
        log_info(
            self.component,
            "Completed synchronous screen monitoring",
            frames=len(frames),
            elapsed=elapsed,
        )

        return {
            "frames": frames,
            "frame_count": len(frames),
            "prompt": prompt_text,
            "duration": elapsed,
            "interval": interval_value,
        }

    async def start_live_monitoring(
        self,
        prompt: Optional[str] = None,
        interval: Optional[float] = None,
        monitor: int = 1,
        callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        max_frames: Optional[int] = None,
        save_images: bool = False,
    ) -> asyncio.Task:
        """Start an asynchronous monitoring loop and stream results."""

        if self.is_running:
            raise RuntimeError("Screen monitoring is already running")

        interval_value = interval or self.capture_interval
        prompt_text = prompt.strip() if prompt else self.DEFAULT_PROMPT
        self._stop_event = asyncio.Event()

        async def _loop() -> None:
            frame_index = 0
            try:
                while True:
                    if self._stop_event and self._stop_event.is_set():
                        break

                    frame_result = await asyncio.to_thread(
                        self.analyze_current_screen,
                        prompt_text,
                        monitor,
                        save_images,
                    )
                    frame_index += 1
                    frame_result["iteration"] = frame_index

                    if callback:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(frame_result)
                        else:
                            await asyncio.to_thread(callback, frame_result)

                    if max_frames and frame_index >= max_frames:
                        break

                    try:
                        if self._stop_event:
                            await asyncio.wait_for(
                                self._stop_event.wait(), timeout=interval_value
                            )
                    except asyncio.TimeoutError:
                        continue
            finally:
                log_info(
                    self.component,
                    "Live monitoring loop terminated",
                    frames=frame_index,
                )
                self._monitor_task = None
                self._stop_event = None

        log_info(
            self.component,
            "Starting live monitoring loop",
            interval=interval_value,
            monitor=monitor,
            max_frames=max_frames,
        )

        self._monitor_task = asyncio.create_task(_loop())
        return self._monitor_task

    async def stop_live_monitoring(self) -> None:
        """Stop the asynchronous monitoring loop if it is running."""

        if self._stop_event and not self._stop_event.is_set():
            self._stop_event.set()

        if self._monitor_task:
            try:
                await self._monitor_task
            except Exception as exc:  # pragma: no cover - defensive logging
                log_error(
                    self.component,
                    f"Error stopping live monitoring: {exc}",
                )
            finally:
                self._monitor_task = None
                self._stop_event = None

    def _capture_frame(self, monitor: int, save_image: bool) -> Dict[str, Any]:
        if mss is None:
            raise RuntimeError(
                "mss dependency is unavailable for screen capture"
            )

        with mss.mss() as sct:
            monitors = sct.monitors
            if not monitors:
                raise RuntimeError("No monitors detected for screen capture")

            # Index 0 is the virtual monitor covering all screens.
            monitor_index = monitor
            if monitor_index >= len(monitors):
                monitor_index = 1 if len(monitors) > 1 else 0

            frame = sct.grab(monitors[monitor_index])

        image = Image.frombytes("RGB", frame.size, frame.rgb)
        path_str: Optional[str] = None
        if save_image:
            path_str = self._save_image(image)

        return {"image": image, "path": path_str}

    def _save_image(self, image: Image.Image) -> str:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
        path = self.save_directory / f"screen_{timestamp}.png"
        image.save(path)
        log_file_operation(
            self.component,
            "Captured live screenshot",
            str(path),
            "create",
        )
        return str(path)

    @staticmethod
    def _encode_image(image: Image.Image) -> str:
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def _query_ollama(self, prompt: str, image_b64: str) -> Optional[str]:
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image", "image": image_b64},
                    ],
                }
            ],
            "stream": False,
        }

        try:
            response = requests.post(
                self.ollama_url,
                json=payload,
                timeout=self.request_timeout,
            )
            response.raise_for_status()
            data = response.json()
            message = data.get("message", {})
            content = message.get("content")

            if isinstance(content, str):
                return content

            if isinstance(content, list):
                parts = [
                    item.get("text", "")
                    for item in content
                    if isinstance(item, dict)
                ]
                return "".join(parts)

            return None
        except requests.RequestException as exc:
            log_error(self.component, f"Ollama request failed: {exc}")
        except Exception as exc:  # pragma: no cover
            log_error(
                self.component,
                f"Unexpected Ollama response error: {exc}",
            )

        return None
