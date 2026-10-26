#!/usr/bin/env python3
"""
Maverick Auto-Improvement Engine
Integrates with ULTRON Agent 3.0 to provide continuous self-improvement capabilities
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum

from ultron_multi_ai_router import UltronMultiAIRouter
from utils.event_system import EventSystem


class ImprovementStatus(Enum):
    SUGGESTED = "suggested"
    APPROVED = "approved"
    APPLIED = "applied"
    REJECTED = "rejected"
    FAILED = "failed"


@dataclass
class ImprovementSuggestion:
    """Represents a single improvement suggestion from Maverick"""
    id: str
    timestamp: datetime
    file_path: str
    suggestion_type: str  # "bug_fix", "optimization", "feature", "refactor"
    priority: int  # 1-10, 10 being highest
    description: str
    code_changes: Dict[str, str]  # old_code -> new_code
    impact_assessment: str
    confidence_score: float  # 0.0 - 1.0
    status: ImprovementStatus = ImprovementStatus.SUGGESTED
    ai_reasoning: str = ""
    test_results: Optional[str] = None

    def to_dict(self) -> Dict:
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        result['status'] = self.status.value
        return result

    @classmethod
    def from_dict(cls, data: Dict) -> 'ImprovementSuggestion':
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        data['status'] = ImprovementStatus(data['status'])
        return cls(**data)


class MaverickEngine:
    """
    The heart of ULTRON's self-improvement system
    Continuously analyzes code, suggests improvements, and applies approved changes
    """

    def __init__(self, config: Dict, event_system: EventSystem):
        self.config = config
        self.event_system = event_system
        self.ai_router = UltronMultiAIRouter()
        self.logger = logging.getLogger(__name__)

        # State management
        self.suggestions: List[ImprovementSuggestion] = []
        self.running = False
        self.analysis_interval = config.get('maverick_analysis_interval', 300)  # 5 minutes
        self.auto_apply_threshold = config.get('maverick_auto_apply_threshold', 0.9)

        # File paths
        self.project_root = Path(".")
        self.suggestions_file = self.project_root / "maverick_suggestions.json"
        self.analysis_log = self.project_root / "maverick_analysis.log"

        # Setup logging
        self._setup_logging()

        # Load existing suggestions
        self._load_suggestions()

        self.logger.info("🚀 Maverick Engine initialized")

    def _setup_logging(self):
        """Setup dedicated Maverick logging"""
        handler = logging.FileHandler(self.analysis_log)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - MAVERICK - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def _load_suggestions(self):
        """Load existing suggestions from storage"""
        try:
            if self.suggestions_file.exists():
                with open(self.suggestions_file, 'r') as f:
                    data = json.load(f)
                    self.suggestions = [
                        ImprovementSuggestion.from_dict(s) for s in data
                    ]
                self.logger.info(f"Loaded {len(self.suggestions)} existing suggestions")
        except Exception as e:
            self.logger.error(f"Failed to load suggestions: {e}")

    def _save_suggestions(self):
        """Save suggestions to storage"""
        try:
            with open(self.suggestions_file, 'w') as f:
                json.dump([s.to_dict() for s in self.suggestions], f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save suggestions: {e}")

    async def start_monitoring(self):
        """Start the continuous monitoring and improvement loop"""
        if self.running:
            self.logger.warning("Maverick already running")
            return

        self.running = True
        self.logger.info("🎯 Starting Maverick continuous monitoring")

        # Emit start event
        await self.event_system.emit("maverick_started", {
            "timestamp": datetime.now().isoformat(),
            "analysis_interval": self.analysis_interval
        })

        try:
            while self.running:
                await self._analysis_cycle()
                await asyncio.sleep(self.analysis_interval)
        except Exception as e:
            self.logger.error(f"Maverick monitoring error: {e}")
            self.running = False

    async def stop_monitoring(self):
        """Stop the monitoring loop"""
        self.running = False
        self.logger.info("🛑 Maverick monitoring stopped")

        await self.event_system.emit("maverick_stopped", {
            "timestamp": datetime.now().isoformat()
        })

    async def _analysis_cycle(self):
        """Single cycle of analysis and improvement detection"""
        self.logger.info("🔍 Starting analysis cycle")

        try:
            # 1. Scan for files to analyze
            files_to_analyze = await self._get_files_for_analysis()

            # 2. Analyze each file
            for file_path in files_to_analyze:
                await self._analyze_file(file_path)

            # 3. Process high-confidence suggestions
            await self._process_auto_apply_suggestions()

            # 4. Emit analysis complete event
            await self.event_system.emit("maverick_analysis_complete", {
                "files_analyzed": len(files_to_analyze),
                "new_suggestions": len([s for s in self.suggestions
                                     if s.status == ImprovementStatus.SUGGESTED]),
                "timestamp": datetime.now().isoformat()
            })

            self.logger.info(f"✅ Analysis cycle complete - {len(files_to_analyze)} files analyzed")

        except Exception as e:
            self.logger.error(f"Analysis cycle failed: {e}")
            await self.event_system.emit("maverick_error_detected", {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })

    async def _get_files_for_analysis(self) -> List[Path]:
        """Get list of Python files that should be analyzed"""
        files = []

        # Focus on core system files
        core_patterns = [
            "*.py",
            "tools/*.py",
            "utils/*.py"
        ]

        for pattern in core_patterns:
            files.extend(self.project_root.glob(pattern))

        # Filter out test files and cache
        filtered_files = [
            f for f in files
            if not any(skip in str(f) for skip in [
                "test_", "__pycache__", ".pyc", "venv", ".venv"
            ])
        ]

        return filtered_files[:10]  # Limit to prevent overload

    async def _analyze_file(self, file_path: Path):
        """Analyze a single file for improvement opportunities"""
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if len(content) < 100:  # Skip tiny files
                return

            # Build analysis prompt
            prompt = self._build_analysis_prompt(file_path, content)

            # Get AI analysis using Llama 4 Maverick
            response = await self.ai_router.get_improvement_suggestions(prompt)

            if not response or not response.get('suggestions'):
                return

            # Parse and store suggestions
            for suggestion_data in response['suggestions']:
                suggestion = self._parse_suggestion(file_path, suggestion_data)
                if suggestion and self._is_novel_suggestion(suggestion):
                    self.suggestions.append(suggestion)
                    self.logger.info(f"💡 New suggestion for {file_path}: {suggestion.description}")

                    # Emit event
                    await self.event_system.emit("maverick_improvement_suggested", {
                        "file": str(file_path),
                        "suggestion": suggestion.to_dict()
                    })

            # Save suggestions
            self._save_suggestions()

        except Exception as e:
            self.logger.error(f"Failed to analyze {file_path}: {e}")

    def _build_analysis_prompt(self, file_path: Path, content: str) -> str:
        """Build the analysis prompt for AI"""
        return f"""
Analyze this Python file for potential improvements. Focus on:
1. Performance optimizations
2. Code quality issues
3. Bug prevention
4. Security vulnerabilities
5. Maintainability improvements

File: {file_path}

Code:
```python
{content[:3000]}  # Limit to prevent token overflow
```

Provide specific, actionable suggestions with:
- Clear description of the improvement
- Priority level (1-10)
- Code changes needed
- Impact assessment
- Confidence score (0.0-1.0)

Return suggestions in JSON format:
{{
    "suggestions": [
        {{
            "type": "optimization|bug_fix|refactor|feature",
            "priority": 8,
            "description": "Clear description",
            "old_code": "code to replace",
            "new_code": "replacement code",
            "impact": "expected impact",
            "confidence": 0.85,
            "reasoning": "why this improvement helps"
        }}
    ]
}}
"""

    def _parse_suggestion(self, file_path: Path, data: Dict) -> Optional[ImprovementSuggestion]:
        """Parse AI response into ImprovementSuggestion"""
        try:
            suggestion_id = f"{file_path.stem}_{int(time.time())}"

            return ImprovementSuggestion(
                id=suggestion_id,
                timestamp=datetime.now(),
                file_path=str(file_path),
                suggestion_type=data.get('type', 'optimization'),
                priority=min(10, max(1, data.get('priority', 5))),
                description=data.get('description', ''),
                code_changes={
                    data.get('old_code', ''): data.get('new_code', '')
                },
                impact_assessment=data.get('impact', ''),
                confidence_score=min(1.0, max(0.0, data.get('confidence', 0.5))),
                ai_reasoning=data.get('reasoning', '')
            )
        except Exception as e:
            self.logger.error(f"Failed to parse suggestion: {e}")
            return None

    def _is_novel_suggestion(self, new_suggestion: ImprovementSuggestion) -> bool:
        """Check if this is a genuinely new suggestion"""
        for existing in self.suggestions:
            if (existing.file_path == new_suggestion.file_path and
                existing.description == new_suggestion.description):
                return False
        return True

    async def _process_auto_apply_suggestions(self):
        """Process high-confidence suggestions for auto-application"""
        auto_apply_suggestions = [
            s for s in self.suggestions
            if (s.status == ImprovementStatus.SUGGESTED and
                s.confidence_score >= self.auto_apply_threshold and
                s.priority >= 7)
        ]

        for suggestion in auto_apply_suggestions[:3]:  # Limit auto-applies
            if await self._auto_apply_suggestion(suggestion):
                self.logger.info(f"🚀 Auto-applied: {suggestion.description}")

    async def _auto_apply_suggestion(self, suggestion: ImprovementSuggestion) -> bool:
        """Attempt to automatically apply a suggestion"""
        try:
            file_path = Path(suggestion.file_path)

            # Read current file content
            with open(file_path, 'r', encoding='utf-8') as f:
                current_content = f.read()

            # Apply code changes
            new_content = current_content
            for old_code, new_code in suggestion.code_changes.items():
                if old_code in current_content:
                    new_content = new_content.replace(old_code, new_code, 1)
                else:
                    self.logger.warning(f"Code to replace not found in {file_path}")
                    return False

            # Create backup
            backup_path = file_path.with_suffix(f".backup_{int(time.time())}")
            backup_path.write_text(current_content)

            # Apply changes
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            # Update suggestion status
            suggestion.status = ImprovementStatus.APPLIED
            suggestion.test_results = "Auto-applied successfully"

            # Emit event
            await self.event_system.emit("maverick_changes_applied", {
                "suggestion_id": suggestion.id,
                "file": suggestion.file_path,
                "description": suggestion.description
            })

            self._save_suggestions()
            return True

        except Exception as e:
            self.logger.error(f"Failed to auto-apply suggestion: {e}")
            suggestion.status = ImprovementStatus.FAILED
            return False

    def get_suggestion_summary(self) -> Dict[str, Any]:
        """Get summary of all suggestions"""
        summary = {
            "total_suggestions": len(self.suggestions),
            "by_status": {},
            "by_priority": {},
            "recent_suggestions": []
        }

        # Count by status
        for status in ImprovementStatus:
            count = len([s for s in self.suggestions if s.status == status])
            summary["by_status"][status.value] = count

        # Count by priority
        for i in range(1, 11):
            count = len([s for s in self.suggestions if s.priority == i])
            if count > 0:
                summary["by_priority"][i] = count

        # Recent suggestions
        recent = sorted(self.suggestions, key=lambda x: x.timestamp, reverse=True)[:5]
        summary["recent_suggestions"] = [
            {
                "id": s.id,
                "description": s.description,
                "priority": s.priority,
                "status": s.status.value,
                "file": s.file_path
            }
            for s in recent
        ]

        return summary

    async def force_analysis(self, file_path: str = None) -> Dict[str, Any]:
        """Force immediate analysis of specific file or all files"""
        self.logger.info(f"🔥 Force analysis triggered for: {file_path or 'all files'}")

        if file_path:
            await self._analyze_file(Path(file_path))
        else:
            await self._analysis_cycle()

        return self.get_suggestion_summary()


# Convenience functions for integration
async def create_maverick_engine(config: Dict, event_system: EventSystem) -> MaverickEngine:
    """Factory function to create and initialize Maverick engine"""
    engine = MaverickEngine(config, event_system)
    return engine


def get_maverick_status() -> str:
    """Get current Maverick system status"""
    suggestions_file = Path("maverick_suggestions.json")
    if suggestions_file.exists():
        with open(suggestions_file) as f:
            data = json.load(f)
            return f"Maverick: {len(data)} suggestions tracked"
    return "Maverick: No suggestions yet"


if __name__ == "__main__":
    # Test run
    from utils.event_system import EventSystem
    import asyncio

    async def main():
        config = {"maverick_analysis_interval": 60}
        event_system = EventSystem()

        engine = await create_maverick_engine(config, event_system)

        # Run one analysis cycle
        await engine._analysis_cycle()

        print("Maverick analysis complete! - maverick_engine.py:453")
        print(json.dumps(engine.get_suggestion_summary(), indent=2))

    asyncio.run(main())
