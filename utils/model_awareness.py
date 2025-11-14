"""
ULTRON Agent Model Awareness System
Provides AI model coordination and file modification safety checks
"""

import os
import json
import hashlib
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional, Set
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
from utils.ultron_logger import ultron_logger

class ModelCapability(Enum):
    """Supported model capabilities"""
    CODE_GENERATION = "code_generation"
    CODE_ANALYSIS = "code_analysis"
    VISION = "vision"
    MULTIMODAL = "multimodal"
    REASONING = "reasoning"
    FAST_INFERENCE = "fast_inference"

@dataclass
class ModelProfile:
    """Profile of an AI model's capabilities and performance"""
    name: str
    capabilities: List[ModelCapability]
    context_window: int  # Max tokens
    avg_latency_ms: float
    cost_per_1k_tokens: float = 0.0
    reliability_score: float = 1.0  # 0.0 to 1.0

@dataclass
class FileContext:
    """Represents the context of a file for modification decisions"""
    file_path: str
    last_modified: datetime
    size: int
    hash: str
    dependencies: List[str]
    related_files: List[str]
    recent_changes: List[Dict[str, Any]]
    stability_score: float  # 0.0 to 1.0, higher is more stable

@dataclass
class ModificationDecision:
    """Represents a decision about whether to modify a file"""
    should_proceed: bool
    reason: str
    confidence: float
    context: FileContext
    recommendations: List[str]

@dataclass
class PerformanceMetrics:
    """Performance metrics for a model"""
    model_name: str
    avg_latency_ms: float
    success_rate: float
    token_efficiency: float  # Tokens per millisecond

class ModelAwareness:
    """
    AI Model Awareness System for ULTRON Agent
    Coordinates file modifications and ensures system stability
    """

    def __init__(self):
        self.logger = ultron_logger
        self.cache_file = Path("cache/model_awareness_cache.json")
        self.cache_duration = timedelta(hours=1)
        self.file_contexts: Dict[str, FileContext] = {}
        self.active_models: Set[str] = set()
        self.modification_history: List[Dict[str, Any]] = []
        self.max_history = 100

        # Model profiles for capability matching
        self.model_profiles: Dict[str, ModelProfile] = self._init_model_profiles()
        self.performance_metrics: Dict[str, PerformanceMetrics] = {}

        # Critical files that require extra caution
        self.critical_files = {
            "agent_core.py",
            "brain.py",
            "config.py",
            "ultron_config.json",
            "main.py",
            "run.bat"
        }

        # File dependencies mapping
        self.file_dependencies = {
            "agent_core.py": ["brain.py", "config.py", "utils/event_system.py"],
            "brain.py": ["config.py", "utils/ultron_logger.py"],
            "config.py": ["ultron_config.json"],
            "gui/ultron_enhanced/web/index.html": ["gui_api_server.py", "api_server.py"]
        }

        self._load_cache()

    def _load_cache(self) -> None:
        """Load cached file contexts"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)

                # Check if cache is still valid
                cache_time = datetime.fromisoformat(data.get('timestamp', '2000-01-01'))
                if datetime.now() - cache_time < self.cache_duration:
                    self.file_contexts = {}
                    for path, context_data in data.get('contexts', {}).items():
                        context_data['last_modified'] = datetime.fromisoformat(context_data['last_modified'])
                        self.file_contexts[path] = FileContext(**context_data)

                    self.logger.log_info("model_awareness", "Loaded cached file contexts")
                else:
                    self.logger.log_info("model_awareness", "Cache expired, will rebuild")
        except Exception as e:
            self.logger.log_error("model_awareness", f"Error loading cache: {str(e)}")

    def _save_cache(self) -> None:
        """Save file contexts to cache"""
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'contexts': {}
            }

            for path, context in self.file_contexts.items():
                context_dict = asdict(context)
                context_dict['last_modified'] = context.last_modified.isoformat()
                cache_data['contexts'][path] = context_dict

            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)

            self.logger.log_info("model_awareness", "Saved file contexts to cache")
        except Exception as e:
            self.logger.log_error("model_awareness", f"Error saving cache: {str(e)}")

    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of file content"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return ""

    def _get_file_dependencies(self, file_path: str) -> List[str]:
        """Get files that depend on the given file"""
        dependencies = []
        file_name = Path(file_path).name

        # Check direct dependencies
        if file_name in self.file_dependencies:
            dependencies.extend(self.file_dependencies[file_name])

        # Check reverse dependencies
        for dep_file, deps in self.file_dependencies.items():
            if file_name in deps:
                dependencies.append(dep_file)

        return list(set(dependencies))

    def _get_related_files(self, file_path: str) -> List[str]:
        """Get files related to the given file"""
        related = []
        file_path_obj = Path(file_path)
        file_name = file_path_obj.name
        file_stem = file_path_obj.stem

        # Find files with similar names or in same directory
        workspace_root = Path(".")
        for file in workspace_root.rglob("*"):
            if file.is_file() and file != file_path_obj:
                # Same directory
                if file.parent == file_path_obj.parent:
                    related.append(str(file))
                # Similar name (same stem)
                elif file.stem == file_stem and file.suffix != file_path_obj.suffix:
                    related.append(str(file))

        return related[:10]  # Limit to 10 related files

    def _calculate_stability_score(self, file_path: str) -> float:
        """Calculate stability score for a file (0.0 to 1.0)"""
        score = 1.0
        file_name = Path(file_path).name

        # Critical files have lower stability
        if file_name in self.critical_files:
            score *= 0.3

        # Recently modified files have lower stability
        if file_path in self.file_contexts:
            context = self.file_contexts[file_path]
            hours_since_modified = (datetime.now() - context.last_modified).total_seconds() / 3600

            if hours_since_modified < 1:
                score *= 0.5
            elif hours_since_modified < 24:
                score *= 0.7

        # Files with many dependencies have lower stability
        dependencies = self._get_file_dependencies(file_path)
        if len(dependencies) > 5:
            score *= 0.6
        elif len(dependencies) > 2:
            score *= 0.8

        return max(0.0, min(1.0, score))

    def check_file_context(self, file_path: str) -> FileContext:
        """
        Get comprehensive context for a file

        Args:
            file_path: Path to the file to analyze

        Returns:
            FileContext object with analysis results
        """
        abs_path = str(Path(file_path).resolve())

        # Check if we have cached context
        if abs_path in self.file_contexts:
            cached_context = self.file_contexts[abs_path]
            # Check if file has been modified since cache
            if Path(abs_path).exists():
                current_mtime = datetime.fromtimestamp(Path(abs_path).stat().st_mtime)
                if current_mtime <= cached_context.last_modified:
                    return cached_context

        # Build new context
        try:
            stat = Path(abs_path).stat()
            file_hash = self._calculate_file_hash(abs_path)
            dependencies = self._get_file_dependencies(abs_path)
            related_files = self._get_related_files(abs_path)
            stability_score = self._calculate_stability_score(abs_path)

            # Get recent changes from history
            recent_changes = []
            for change in self.modification_history[-20:]:  # Last 20 changes
                if change.get('file_path') == abs_path:
                    recent_changes.append(change)

            context = FileContext(
                file_path=abs_path,
                last_modified=datetime.fromtimestamp(stat.st_mtime),
                size=stat.st_size,
                hash=file_hash,
                dependencies=dependencies,
                related_files=related_files,
                recent_changes=recent_changes,
                stability_score=stability_score
            )

            self.file_contexts[abs_path] = context
            self._save_cache()

            self.logger.log_info("model_awareness", f"Analyzed file context for {abs_path}",
                               extra={"stability_score": stability_score})

            return context

        except Exception as e:
            self.logger.log_error("model_awareness", f"Error analyzing file {abs_path}: {str(e)}")

            # Return minimal context for missing/non-existent files
            return FileContext(
                file_path=abs_path,
                last_modified=datetime.now(),
                size=0,
                hash="",
                dependencies=[],
                related_files=[],
                recent_changes=[],
                stability_score=0.0
            )

    def should_modify_file(self, file_path: str, modification_type: str,
                          ai_model: str) -> Tuple[bool, str, FileContext]:
        """
        Determine if a file should be modified

        Args:
            file_path: Path to the file
            modification_type: Type of modification (edit, delete, create)
            ai_model: Name of the AI model requesting modification

        Returns:
            Tuple of (should_proceed, reason, context)
        """
        context = self.check_file_context(file_path)
        file_name = Path(file_path).name

        # Track active model
        self.active_models.add(ai_model)

        # Critical file checks
        if file_name in self.critical_files:
            if modification_type in ['delete', 'replace']:
                return False, f"Critical file {file_name} cannot be {modification_type}d", context

        # Stability checks
        if context.stability_score < 0.3:
            return False, f"File {file_name} has low stability score ({context.stability_score:.2f})", context

        # Recent modification checks
        if context.recent_changes:
            last_change = max(context.recent_changes, key=lambda x: x.get('timestamp', 0))
            change_time = datetime.fromtimestamp(last_change.get('timestamp', 0))
            minutes_since_change = (datetime.now() - change_time).total_seconds() / 60

            if minutes_since_change < 5:
                return False, f"File {file_name} was modified {minutes_since_change:.1f} minutes ago", context

        # Dependency impact assessment
        if len(context.dependencies) > 3:
            reason = f"File {file_name} has {len(context.dependencies)} dependencies - proceed with caution"
            return True, reason, context

        # Model coordination
        if len(self.active_models) > 1:
            other_models = self.active_models - {ai_model}
            reason = f"Multiple AI models active: {', '.join(other_models)} - coordinate modifications"
            return True, reason, context

        return True, "File modification approved", context

    def record_modification(self, file_path: str, modification_type: str,
                           ai_model: str, success: bool = True) -> None:
        """
        Record a file modification in history

        Args:
            file_path: Path to the modified file
            modification_type: Type of modification
            ai_model: Name of the AI model that made the modification
            success: Whether the modification was successful
        """
        record = {
            'timestamp': datetime.now().timestamp(),
            'file_path': str(Path(file_path).resolve()),
            'modification_type': modification_type,
            'ai_model': ai_model,
            'success': success
        }

        self.modification_history.append(record)
        if len(self.modification_history) > self.max_history:
            self.modification_history = self.modification_history[-self.max_history:]

        self.logger.log_file_operation("model_awareness", f"Recorded modification: {modification_type}",
                                     file_path, modification_type)

        # Update context cache
        if record['file_path'] in self.file_contexts:
            del self.file_contexts[record['file_path']]
        self._save_cache()

    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        total_files = len(self.file_contexts)
        critical_files_modified = 0
        recent_modifications = 0

        now = datetime.now()
        for context in self.file_contexts.values():
            file_name = Path(context.file_path).name
            if file_name in self.critical_files:
                hours_since_modified = (now - context.last_modified).total_seconds() / 3600
                if hours_since_modified < 24:
                    critical_files_modified += 1

            if context.recent_changes:
                recent_modifications += len(context.recent_changes)

        return {
            'total_files_analyzed': total_files,
            'critical_files_modified_recently': critical_files_modified,
            'recent_modifications': recent_modifications,
            'active_models': list(self.active_models),
            'system_stability': 'stable' if critical_files_modified == 0 else 'caution'
        }

    def cleanup_old_contexts(self, days: int = 7) -> None:
        """Clean up old file contexts"""
        cutoff = datetime.now() - timedelta(days=days)
        to_remove = []

        for path, context in self.file_contexts.items():
            if context.last_modified < cutoff:
                to_remove.append(path)

        for path in to_remove:
            del self.file_contexts[path]

        self.logger.log_info("model_awareness", f"Cleaned up {len(to_remove)} old contexts")
        self._save_cache()

    def _init_model_profiles(self) -> Dict[str, ModelProfile]:
        """Initialize model capability profiles"""
        return {
            "llava:7b": ModelProfile(
                name="llava:7b",
                capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.VISION, ModelCapability.MULTIMODAL],
                context_window=2048,
                avg_latency_ms=1200
            ),
            "deepseek-r1:14b": ModelProfile(
                name="deepseek-r1:14b",
                capabilities=[ModelCapability.CODE_ANALYSIS, ModelCapability.REASONING],
                context_window=4096,
                avg_latency_ms=2500
            ),
            "gpt-4o": ModelProfile(
                name="gpt-4o",
                capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.VISION, ModelCapability.MULTIMODAL, ModelCapability.REASONING],
                context_window=128000,
                avg_latency_ms=800,
                cost_per_1k_tokens=0.015
            ),
            "amazon.nova-pro-v1:0": ModelProfile(
                name="amazon.nova-pro-v1:0",
                capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.CODE_ANALYSIS],
                context_window=8000,
                avg_latency_ms=600
            )
        }

    def estimate_tokens(self, text: str, model: str = "llava:7b") -> int:
        """
        Estimate token count for text (approximate)
        Uses ~4 characters per token average
        """
        try:
            # Import tiktoken if available for accurate counting
            import tiktoken
            encoding = tiktoken.encoding_for_model(model)
            return len(encoding.encode(text))
        except Exception:
            # Fallback: rough estimate
            return len(text) // 4

    def estimate_cost(self, model: str, tokens: int) -> float:
        """Estimate cost for model usage"""
        profile = self.model_profiles.get(model)
        if not profile or profile.cost_per_1k_tokens == 0:
            return 0.0
        return (tokens / 1000) * profile.cost_per_1k_tokens

    async def get_model_capabilities(self, model: str) -> Dict[str, Any]:
        """Get detailed capabilities of a model"""
        profile = self.model_profiles.get(model)
        if not profile:
            return {"error": f"Unknown model: {model}"}

        return {
            "name": profile.name,
            "capabilities": [c.value for c in profile.capabilities],
            "context_window": profile.context_window,
            "avg_latency_ms": profile.avg_latency_ms,
            "cost_per_1k_tokens": profile.cost_per_1k_tokens,
            "reliability_score": profile.reliability_score
        }

    async def route_to_best_model(self, task_type: str, constraints: Dict[str, Any]) -> str:
        """
        Route task to best available model based on constraints

        Args:
            task_type: Type of task (code_generation, analysis, vision, etc.)
            constraints: Dict with keys like max_latency_ms, max_cost, required_capabilities

        Returns:
            Best model name for the task
        """
        max_latency = constraints.get("max_latency_ms", float('inf'))
        required_capabilities = constraints.get("required_capabilities", [])

        # Convert string capability names to enum
        required_caps = set()
        for cap in required_capabilities:
            try:
                required_caps.add(ModelCapability[cap.upper()])
            except (KeyError, AttributeError):
                pass

        # Find best matching model
        best_model = None
        best_score = -1

        for model_name, profile in self.model_profiles.items():
            # Check if model meets requirements
            if required_caps and not required_caps.issubset(set(profile.capabilities)):
                continue

            if profile.avg_latency_ms > max_latency:
                continue

            # Score based on reliability and latency
            score = profile.reliability_score / (profile.avg_latency_ms / 1000)
            if score > best_score:
                best_score = score
                best_model = model_name

        return best_model or "llava:7b"  # Fallback to default

    def record_performance(self, model: str, latency_ms: float, success: bool) -> None:
        """Record model performance metrics"""
        if model not in self.performance_metrics:
            self.performance_metrics[model] = PerformanceMetrics(
                model_name=model,
                avg_latency_ms=latency_ms,
                success_rate=1.0 if success else 0.0,
                token_efficiency=0.0
            )
        else:
            metrics = self.performance_metrics[model]
            # Update running average
            metrics.avg_latency_ms = (metrics.avg_latency_ms + latency_ms) / 2
            metrics.success_rate = (metrics.success_rate + (1.0 if success else 0.0)) / 2

    def get_performance_metrics(self, model: str) -> Optional[PerformanceMetrics]:
        """Get performance metrics for a model"""
        return self.performance_metrics.get(model)

        for path in to_remove:
            del self.file_contexts[path]

        if to_remove:
            self._save_cache()
            self.logger.log_info("model_awareness", f"Cleaned up {len(to_remove)} old contexts")

# Global instance
_model_awareness_instance: Optional[ModelAwareness] = None

def get_model_awareness() -> ModelAwareness:
    """Get or create global model awareness instance"""
    global _model_awareness_instance
    if _model_awareness_instance is None:
        _model_awareness_instance = ModelAwareness()
    return _model_awareness_instance

# Convenience functions
def should_modify_file(file_path: str, modification_type: str, ai_model: str) -> Tuple[bool, str, FileContext]:
    """Check if a file should be modified"""
    awareness = get_model_awareness()
    return awareness.should_modify_file(file_path, modification_type, ai_model)

def check_file_context(file_path: str) -> FileContext:
    """Get file context"""
    awareness = get_model_awareness()
    return awareness.check_file_context(file_path)

def record_modification(file_path: str, modification_type: str, ai_model: str, success: bool = True) -> None:
    """Record a file modification"""
    awareness = get_model_awareness()
    awareness.record_modification(file_path, modification_type, ai_model, success)
