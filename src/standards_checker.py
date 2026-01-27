import re
from typing import List, Dict, Any, Union


class StandardsChecker:
    """Check code against configured standards and conventions."""

    def __init__(self, config: dict) -> None:
        """Initialize checker with configuration."""
        self.enabled = config.get('rules', {}).get('standards', {}).get('enabled', False)

    def scan(self, file_changes: List[Dict[str, Any]]) -> List[Dict[str, Union[str, int]]]:
        """Scan files for standards violations.
        
        Args:
            file_changes: List of dictionaries with 'file' and 'content' keys
            
        Returns:
            List of violation dictionaries with file, line, severity, type, message, and fix
        """
        violations: List[Dict[str, Union[str, int]]] = []
        if not self.enabled:
            return violations

        for change in file_changes:
            try:
                filename = change.get('file', '')
                content = change.get('content', '')
                if not isinstance(content, str):
                    continue

                lines = content.split('\n')
                for idx, line in enumerate(lines):
                    line_num = idx + 1
                    
                    # Naming checks
                    if re.match(r'^\s*def\s+[A-Z]', line):
                        violations.append(self._create_violation(
                            filename, line_num, 'naming',
                            'Function name should be snake_case',
                            'Rename function to snake_case'
                        ))
                        
                    if re.match(r'^\s*class\s+[a-z]', line):
                        violations.append(self._create_violation(
                            filename, line_num, 'naming', 
                            'Class name should be PascalCase',
                            'Rename class to PascalCase'
                        ))
                    
                    # Bare except check
                    if re.search(r'except\s*:', line):
                        violations.append(self._create_violation(
                            filename, line_num, 'error_handling',
                            'Bare except clause',
                            'Specify exception type or use Exception'
                        ))
                    
                    # Logging check
                    if re.match(r'^\s*def\s+.*:', line):
                        next_idx = idx + 1
                        if next_idx >= len(lines) or 'log' not in lines[next_idx]:
                            violations.append(self._create_violation(
                                filename, line_num, 'missing_logging',
                                'Function missing logging statement',
                                'Add logging statement to function body'
                            ))
                            
            except Exception:
                continue

        return violations

    def _create_violation(self, file: str, line: int, 
                         violation_type: str, message: str, fix: str) -> Dict[str, Union[str, int]]:
        """Helper to create standardized violation dictionary."""
        return {
            'file': file,
            'line': line,
            'severity': 'MEDIUM',
            'type': violation_type,
            'message': message,
            'fix': fix
        }
