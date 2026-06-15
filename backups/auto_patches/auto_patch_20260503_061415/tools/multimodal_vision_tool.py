"""
Multimodal Vision Tool for ULTRON Agent

Integrates vision-language models via NVIDIA NIM for advanced image analysis
while supporting local Ollama-powered screen perception.
"""

import base64
import os
import re
from typing import Any, Dict, Optional

import requests

# ULTRON Agent imports
from utils.ultron_logger import log_error, log_info
from vision import ScreenVisionService

try:
    from utils.event_system import emit_event_sync
    EVENT_SYSTEM_AVAILABLE = True
except ImportError:
    emit_event_sync = None  # type: ignore
    EVENT_SYSTEM_AVAILABLE = False


class MultimodalVisionTool:
    """
    Tool for multimodal vision analysis using NVIDIA NIM vision-language models
    """

    name = "Multimodal Vision Analysis"
    description = (
        "Analyze images using advanced vision-language models via NVIDIA NIM"
    )

    def __init__(self):
        self.nim_api_key = os.environ.get('NVIDIA_NIM_API_KEY', '')
        self.nim_base_url = os.environ.get(
            'NVIDIA_NIM_BASE_URL',
            'https://integrate.api.nvidia.com/v1',
        )
        self.vision_model = os.environ.get(
            'NIM_VISION_MODEL',
            'meta/llama-3.2-11b-vision-instruct',
        )
        self.screen_service: Optional[ScreenVisionService] = None

        try:
            self.screen_service = ScreenVisionService()
        except Exception as exc:
            log_error(
                "multimodal_vision",
                f"Screen vision service unavailable: {exc}",
            )
            self.screen_service = None

    def match(self, command: str) -> bool:
        """Check if command matches vision analysis operations"""
        command_lower = command.lower()
        if self._is_screen_command(command_lower):
            return True

        vision_keywords = (
            "analyze image",
            "vision analysis",
            "multimodal",
            "describe image",
            "image understanding",
            "visual analysis",
            "see image",
        )
        return any(keyword in command_lower for keyword in vision_keywords)

    def execute(self, command: str) -> str:
        """Execute multimodal vision analysis"""
        try:
            command_lower = command.lower()

            if self._is_screen_command(command_lower):
                return self._handle_screen_command(command)

            if (
                "analyze image" in command_lower
                or "describe image" in command_lower
            ):
                # Extract image path if provided
                image_path = self._extract_image_path(command)
                if image_path and os.path.exists(image_path):
                    return self.analyze_image(image_path)
                else:
                    return "Please provide a valid image path for analysis"
            else:
                return self.get_help()

        except Exception as e:
            log_error("multimodal_vision", f"Vision analysis failed: {e}")
            return f"Vision analysis failed: {str(e)}"

    def _is_screen_command(self, command_lower: str) -> bool:
        screen_phrases = (
            "describe screen",
            "current screen",
            "monitor screen",
            "watch screen",
            "live screen",
            "screen analysis",
        )
        if any(phrase in command_lower for phrase in screen_phrases):
            return True

        keywords = ("describe", "monitor", "watch", "analyze", "capture")
        return "screen" in command_lower and any(
            keyword in command_lower for keyword in keywords
        )

    def _handle_screen_command(self, command: str) -> str:
        if not self.screen_service:
            return (
                "Screen vision service unavailable. "
                "Start Ollama and install the `mss` dependency."
            )

        monitor = self._extract_monitor(command)
        prompt = self._extract_prompt(command)
        command_lower = command.lower()

        monitor_keywords = ("monitor", "watch", "stream")
        if any(word in command_lower for word in monitor_keywords):
            duration = self._extract_duration(command) or 15.0
            interval = self._extract_interval(command)

            log_info(
                "multimodal_vision",
                "Starting live screen monitoring",
                duration=duration,
                interval=interval or self.screen_service.capture_interval,
                monitor=monitor,
            )

            results = self.screen_service.monitor_screen(
                prompt=prompt,
                duration=duration,
                interval=interval,
                monitor=monitor,
                save_images=False,
            )
            return self._format_live_results(results, duration)

        log_info(
            "multimodal_vision",
            "Describing current screen via Ollama",
            monitor=monitor,
        )

        result = self.screen_service.analyze_current_screen(
            prompt=prompt,
            monitor=monitor,
            save_image=True,
        )

        analysis = result.get("analysis", "").strip()
        if not analysis:
            return "No description generated for the current screen."

        self._emit_screen_analysis_event(
            analysis=analysis,
            prompt=prompt,
            monitor=monitor,
            image_path=result.get("image_path"),
        )

        image_path = result.get("image_path")
        suffix = f"\n\nSaved to: {image_path}" if image_path else ""
        return f"🖥️ **Current Screen Description**\n{analysis}{suffix}"

    def analyze_image(self, image_path: str) -> str:
        """Analyze an image using NVIDIA NIM vision model"""
        try:
            log_info("multimodal_vision", f"Analyzing image: {image_path}")

            # Load and encode image
            with open(image_path, "rb") as image_file:
                raw_bytes = image_file.read()
            image_data = base64.b64encode(raw_bytes).decode('utf-8')

            # Prepare the analysis prompt
            prompt = """
Analyze this image in detail. Provide:
1. A comprehensive description of what's visible
2. Key objects, people, or elements in the scene
3. Any text or writing present
4. The overall context or setting
5. Notable colors, lighting, or visual characteristics
6. Any actions or activities depicted
7. Potential emotions or mood conveyed
8. Technical details (resolution, format if detectable)

Be thorough but concise in your analysis.
"""

            # Contact NIM vision model
            response = self._contact_nim_vision(prompt, image_data)

            if response:
                return f"🖼️ **Image Analysis Results**\n\n{response}"
            else:
                return "Failed to analyze image via NIM"

        except Exception as e:
            log_error("multimodal_vision", f"Image analysis failed: {e}")
            return f"Image analysis failed: {str(e)}"

    def _contact_nim_vision(
        self,
        prompt: str,
        image_data: str,
    ) -> Optional[str]:
        """Contact NVIDIA NIM vision model"""
        try:
            headers = {
                'Authorization': f'Bearer {self.nim_api_key}',
                'Content-Type': 'application/json'
            }

            # Prepare message with image
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                }
            ]

            payload = {
                'model': self.vision_model,
                'messages': messages,
                'max_tokens': 1000,
                'temperature': 0.7
            }

            response = requests.post(
                f"{self.nim_base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                log_error(
                    "multimodal_vision",
                    "NIM vision API error",
                    status_code=response.status_code,
                    response_text=response.text,
                )
                return None

        except Exception as e:
            log_error("multimodal_vision", f"NIM vision contact failed: {e}")
            return None

    def _extract_image_path(self, command: str) -> Optional[str]:
        """Extract image path from command"""
        # Look for file paths in the command
        path_match = re.search(
            r'["\']([^"\']+\.(?:png|jpg|jpeg|gif|bmp|webp))["\']',
            command,
            re.IGNORECASE,
        )
        if path_match:
            return path_match.group(1)

        # Look for common image file patterns
        words = command.split()
        for word in words:
            extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
            if any(word.lower().endswith(ext) for ext in extensions):
                return word

        return None

    def _extract_prompt(self, command: str) -> Optional[str]:
        prompt_match = re.search(
            r'prompt\s*[:=]\s*(.+)',
            command,
            re.IGNORECASE,
        )
        if prompt_match:
            return prompt_match.group(1).strip()
        return None

    def _extract_duration(self, command: str) -> Optional[float]:
        seconds_match = re.search(
            r'(\d+(?:\.\d+)?)\s*(seconds|second|secs|s)\b',
            command,
            re.IGNORECASE,
        )
        if seconds_match:
            return float(seconds_match.group(1))

        minutes_match = re.search(
            r'(\d+(?:\.\d+)?)\s*(minutes|minute|mins|m)\b',
            command,
            re.IGNORECASE,
        )
        if minutes_match:
            return float(minutes_match.group(1)) * 60.0

        return None

    def _extract_interval(self, command: str) -> Optional[float]:
        interval_match = re.search(
            r'every\s+(\d+(?:\.\d+)?)\s*(seconds|second|secs|s)\b',
            command,
            re.IGNORECASE,
        )
        if interval_match:
            return float(interval_match.group(1))
        return None

    def _extract_monitor(self, command: str) -> int:
        monitor_match = re.search(r'monitor\s*(\d+)', command, re.IGNORECASE)
        if monitor_match:
            return max(0, int(monitor_match.group(1)))

        screen_match = re.search(r'screen\s*(\d+)', command, re.IGNORECASE)
        if screen_match:
            return max(0, int(screen_match.group(1)))

        return 1

    def _format_live_results(
        self,
        results: Dict[str, Any],
        duration: float,
    ) -> str:
        frames = results.get("frames", [])
        if not frames:
            return "No frames were analyzed during screen monitoring."

        lines = []
        for frame in frames:
            analysis = frame.get("analysis", "").strip()
            if not analysis:
                continue
            iteration = frame.get("iteration")
            captured = frame.get("captured_at", "")
            label = f"Frame {iteration}" if iteration else "Frame"
            lines.append(f"{label} ({captured}):\n{analysis}")

        summary = "\n\n".join(lines) if lines else "No analysis text produced."

        frame_count = results.get("frame_count", len(frames))
        interval_value = results.get("interval")

        header_lines = [
            "🖥️ **Live Screen Monitor**",
            f"Frames analyzed: {frame_count}",
            f"Duration: {duration:.1f}s",
        ]
        if interval_value:
            header_lines.insert(2, f"Interval: {interval_value:.1f}s")

        header = "\n".join(header_lines)
        return f"{header}\n\n{summary}"

    def _emit_screen_analysis_event(
        self,
        *,
        analysis: str,
        prompt: Optional[str],
        monitor: int,
        image_path: Optional[str],
    ) -> None:
        """Broadcast screen analysis so the voice system can narrate it."""
        if not EVENT_SYSTEM_AVAILABLE or not emit_event_sync:
            return

        try:
            payload = {
                "analysis": analysis,
                "prompt": prompt,
                "monitor": monitor,
                "image_path": image_path,
                "source": "multimodal_vision_tool",
            }
            emit_event_sync(
                "screen_analysis_result",
                payload,
                source="multimodal_vision",
            )
        except Exception as exc:
            log_error(
                "multimodal_vision",
                f"Failed to emit screen analysis event: {exc}",
            )

    def get_help(self) -> str:
        """Get help information for the tool"""
        return """
🤖 **Multimodal Vision Analysis Tool**

**Capabilities:**
• Advanced image understanding using vision-language models
• Detailed scene description and analysis
• Text recognition and extraction
• Object detection and identification
• Contextual understanding

**Usage Examples:**
• "analyze image screenshot_20231006_123456.png"
• "describe image 'path/to/photo.jpg'"
• "visual analysis of image.png"

**Supported Formats:** PNG, JPG, JPEG, GIF, BMP, WebP

**Requirements:**
• NVIDIA_NIM_API_KEY environment variable set
• Valid image file path
• Network connection for NIM API
"""

    @classmethod
    def schema(cls):
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": (
                            "Vision analysis command with image path"
                        )
                    }
                },
                "required": ["command"]
            }
        }
