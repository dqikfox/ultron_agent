"""
ULTRON Agent - Production-Grade Safety & Policy Engine
Enforces JSON-based policies for file access, command execution, and network requests
"""

import json
import pathlib
import re
import subprocess
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

try:
    from utils.ultron_logger import log_info, log_error
    # log_warning may not exist, create fallback
    def log_warning(component, msg):
        log_info(component, f"WARNING: {msg}")
except ImportError:
    # Fallback if ultron_logger not available
    import logging
    logger = logging.getLogger(__name__)
    def log_info(component, msg):
        logger.info(f"[{component}] {msg}")
    def log_error(component, msg, exception=None):
        logger.error(f"[{component}] {msg}", exc_info=exception)
    def log_warning(component, msg):
        logger.warning(f"[{component}] {msg}")


@dataclass
class FileAccessPolicy:
    """File access restrictions"""
    allowed_base_paths: List[str]
    blocked_paths: List[str]
    max_file_size_mb: int
    require_confirmation: Dict[str, bool]


@dataclass
class CommandPolicy:
    """Command execution restrictions"""
    allowed_commands: List[str]
    blocked_commands: List[str]
    max_execution_time_seconds: int
    require_confirmation: bool
    network_access: str


@dataclass
class SecurityPolicy:
    """Overall security settings"""
    log_all_actions: bool
    require_user_confirmation_destructive: bool
    sandbox_mode: bool
    allow_code_execution: bool
    encryption_at_rest: bool = False  # Optional field


class SafetyEngine:
    """
    Production-grade safety enforcement for ULTRON Agent

    Features:
    - Path validation against allow/block lists
    - Command whitelist/blacklist
    - Resource limits
    - Confirmation prompts
    - Audit logging
    """

    def __init__(self, policy_path: str = "policy/policies.json"):
        self.policy_path = policy_path
        self.policy_data = self._load_policy()

        # Parse policy sections
        self.file_policy = FileAccessPolicy(**self.policy_data["file_access"])
        self.cmd_policy = CommandPolicy(**self.policy_data["command_execution"])
        self.security = SecurityPolicy(**self.policy_data["security"])

        log_info("safety_engine", f"Loaded policies from {policy_path}")

    def _load_policy(self) -> Dict:
        """Load and validate policy JSON"""
        try:
            with open(self.policy_path, 'r') as f:
                data = json.load(f)

            # Validate required sections
            required = ["file_access", "command_execution", "security"]
            for section in required:
                if section not in data:
                    raise ValueError(f"Missing policy section: {section}")

            return data
        except FileNotFoundError:
            log_error("safety_engine", f"Policy file not found: {self.policy_path}")
            raise
        except json.JSONDecodeError as e:
            log_error("safety_engine", f"Invalid JSON in policy file: {e}")
            raise

    def reload_policy(self):
        """Hot-reload policies from disk"""
        log_info("safety_engine", "Reloading policies...")
        self.policy_data = self._load_policy()
        self.file_policy = FileAccessPolicy(**self.policy_data["file_access"])
        self.cmd_policy = CommandPolicy(**self.policy_data["command_execution"])

    # ═══════════════════════════════════════════════════════════════
    # FILE ACCESS VALIDATION
    # ═══════════════════════════════════════════════════════════════

    def validate_file_path(self, path: str, operation: str = "read") -> Tuple[bool, str, Optional[pathlib.Path]]:
        """
        Validate file path against allow/block lists

        Args:
            path: Path to validate
            operation: 'read', 'write', 'delete', or 'execute'

        Returns:
            (is_allowed, message, resolved_path)
        """
        try:
            # Resolve to absolute path
            resolved = pathlib.Path(path).expanduser().resolve()

            # Check blocked paths first
            for blocked in self.file_policy.blocked_paths:
                blocked_path = pathlib.Path(blocked).resolve()
                if str(resolved).startswith(str(blocked_path)):
                    msg = f"❌ Access denied: {path} is in blocked directory {blocked}"
                    log_warning("safety_engine", msg)
                    return False, msg, None

            # Check allowed base paths
            is_allowed = False
            for allowed in self.file_policy.allowed_base_paths:
                allowed_path = pathlib.Path(allowed).expanduser().resolve()
                if str(resolved).startswith(str(allowed_path)):
                    is_allowed = True
                    break

            if not is_allowed:
                msg = f"❌ Access denied: {path} is outside allowed directories"
                log_warning("safety_engine", msg)
                return False, msg, None

            # Check file size for read operations
            if operation == "read" and resolved.exists():
                size_mb = resolved.stat().st_size / (1024 * 1024)
                if size_mb > self.file_policy.max_file_size_mb:
                    msg = f"❌ File too large: {size_mb:.1f}MB > {self.file_policy.max_file_size_mb}MB limit"
                    log_warning("safety_engine", msg)
                    return False, msg, None

            # Check if confirmation required
            needs_confirmation = self.file_policy.require_confirmation.get(operation, False)

            msg = f"✅ Path validated: {resolved}"
            if needs_confirmation:
                msg += " (requires confirmation)"

            log_info("safety_engine", f"File access validated: {operation} {path}")
            return True, msg, resolved

        except Exception as e:
            msg = f"❌ Path validation error: {e}"
            log_error("safety_engine", msg, exception=e)
            return False, msg, None

    # ═══════════════════════════════════════════════════════════════
    # COMMAND EXECUTION VALIDATION
    # ═══════════════════════════════════════════════════════════════

    def validate_command(self, command: str) -> Tuple[bool, str]:
        """
        Validate command against whitelist/blacklist

        Args:
            command: Shell command to validate

        Returns:
            (is_allowed, message)
        """
        # Check blocked commands first (highest priority)
        for blocked_pattern in self.cmd_policy.blocked_commands:
            if re.search(blocked_pattern, command):
                msg = f"❌ Blocked dangerous command: {command}"
                log_warning("safety_engine", msg)
                return False, msg

        # Check allowed commands
        is_allowed = False
        for allowed_pattern in self.cmd_policy.allowed_commands:
            # Convert glob patterns to regex
            regex_pattern = allowed_pattern.replace("*", ".*")
            if re.match(regex_pattern, command):
                is_allowed = True
                break

        if not is_allowed:
            msg = f"❌ Command not in whitelist: {command}"
            log_warning("safety_engine", msg)
            return False, msg

        msg = f"✅ Command validated: {command}"
        if self.cmd_policy.require_confirmation:
            msg += " (requires confirmation)"

        log_info("safety_engine", f"Command validated: {command}")
        return True, msg

    def execute_safe_command(self, command: str, timeout: Optional[int] = None) -> Tuple[bool, str, str]:
        """
        Execute command with safety checks

        Args:
            command: Command to execute
            timeout: Override default timeout

        Returns:
            (success, stdout, stderr)
        """
        # Validate first
        is_valid, msg = self.validate_command(command)
        if not is_valid:
            return False, "", msg

        # Use policy timeout if not specified
        timeout = timeout or self.cmd_policy.max_execution_time_seconds

        try:
            log_info("safety_engine", f"Executing: {command}")
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False
            )

            success = result.returncode == 0
            log_info("safety_engine", f"Command {'succeeded' if success else 'failed'} with code {result.returncode}")

            return success, result.stdout, result.stderr

        except subprocess.TimeoutExpired:
            msg = f"❌ Command timeout after {timeout}s: {command}"
            log_error("safety_engine", msg)
            return False, "", msg
        except Exception as e:
            msg = f"❌ Command execution error: {e}"
            log_error("safety_engine", msg, exception=e)
            return False, "", str(e)

    # ═══════════════════════════════════════════════════════════════
    # NETWORK ACCESS VALIDATION
    # ═══════════════════════════════════════════════════════════════

    def validate_network_request(self, url: str) -> Tuple[bool, str]:
        """
        Validate network request against allowed domains

        Args:
            url: URL to validate

        Returns:
            (is_allowed, message)
        """
        import urllib.parse

        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc or parsed.path.split('/')[0]

        # Check against allowed domains
        allowed_domains = self.policy_data.get("network_access", {}).get("allowed_domains", [])

        for allowed in allowed_domains:
            if allowed.startswith("*"):
                # Wildcard domain (e.g., *.azure.com)
                if domain.endswith(allowed[1:]):
                    log_info("safety_engine", f"Network request allowed: {url}")
                    return True, f"✅ Domain allowed: {domain}"
            elif domain == allowed:
                log_info("safety_engine", f"Network request allowed: {url}")
                return True, f"✅ Domain allowed: {domain}"

        msg = f"❌ Domain not allowed: {domain}"
        log_warning("safety_engine", msg)
        return False, msg

    # ═══════════════════════════════════════════════════════════════
    # AUDIT & MONITORING
    # ═══════════════════════════════════════════════════════════════

    def log_action(self, action_type: str, details: Dict):
        """Log security-relevant actions for audit"""
        if self.security.log_all_actions:
            log_info("safety_audit", f"{action_type}: {json.dumps(details)}")

    def get_policy_summary(self) -> str:
        """Return human-readable policy summary"""
        return f"""
╔══════════════════════════════════════════════════════════════╗
║               ULTRON SAFETY POLICIES ACTIVE                 ║
╚══════════════════════════════════════════════════════════════╝

📁 File Access:
   Allowed: {len(self.file_policy.allowed_base_paths)} base paths
   Blocked: {len(self.file_policy.blocked_paths)} directories
   Max Size: {self.file_policy.max_file_size_mb} MB

💻 Commands:
   Whitelist: {len(self.cmd_policy.allowed_commands)} patterns
   Blacklist: {len(self.cmd_policy.blocked_commands)} dangerous commands
   Timeout: {self.cmd_policy.max_execution_time_seconds}s
   Confirmation: {'Required' if self.cmd_policy.require_confirmation else 'Not required'}

🔒 Security:
   Sandbox Mode: {'Enabled' if self.security.sandbox_mode else 'Disabled'}
   Audit Logging: {'Enabled' if self.security.log_all_actions else 'Disabled'}
   Code Execution: {'Allowed' if self.security.allow_code_execution else 'Blocked'}
"""


# ═══════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════

_global_safety_engine = None

def get_safety_engine() -> SafetyEngine:
    """Get or create global safety engine instance"""
    global _global_safety_engine
    if _global_safety_engine is None:
        _global_safety_engine = SafetyEngine()
    return _global_safety_engine


if __name__ == "__main__":
    # Test the safety engine
    engine = SafetyEngine()
    print(engine.get_policy_summary())

    # Test file validation
    print("\n🧪 Testing file validation:")
    tests = [
        ("/home/ultro/projects/test.py", "read"),
        ("/etc/passwd", "read"),
        ("/home/ultro/Documents/notes.txt", "write"),
    ]
    for path, op in tests:
        valid, msg, resolved = engine.validate_file_path(path, op)
        print(f"  {msg}")

    # Test command validation
    print("\n🧪 Testing command validation:")
    commands = [
        "ls -la",
        "rm -rf /",
        "python3 test.py",
        "sudo apt-get install malware",
    ]
    for cmd in commands:
        valid, msg = engine.validate_command(cmd)
        print(f"  {msg}")
