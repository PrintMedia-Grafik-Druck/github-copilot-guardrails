import json
import sys
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Literal


class AuditLogger:
    """Logs code scan results in structured format with thread-safe file operations."""

    _lock = threading.Lock()

    def __init__(self) -> None:
        """Initialize logger and ensure log directory exists."""
        self.log_file = Path("logs/audit.log")
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def log_scan(
        self,
        pr_number: str,
        commit_sha: str,
        findings: List[Dict[str, Any]],
        policy_action: Literal["APPROVED", "WARNED", "BLOCKED"],
    ) -> None:
        """Record a code scan event with metadata and results.

        Args:
            pr_number: Associated pull request identifier
            commit_sha: Git commit hash that was analyzed
            findings: List of security/code quality findings
            policy_action: Final enforcement decision based on findings
        """
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "pr_number": pr_number,
            "commit_sha": commit_sha,
            "findings": findings,
            "policy_action": policy_action,
        }

        with self._lock:
            try:
                with self.log_file.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(log_data) + "\n")
            except OSError as e:
                print(f"Audit log write failed: {e}", file=sys.stderr)
