import re
from typing import List, Dict, Any

class SecurityScanner:
    """Scans code files for common security vulnerabilities based on predefined rules."""
    
    def __init__(self) -> None:
        self.rules: List[Dict[str, Any]] = [
            {
                'regex': re.compile(r"(password|api_key|secret|token)\s*=\s*['\"][^'\"]+['\"]"),
                'severity': 'CRITICAL',
                'owasp': 'A02: Cryptographic Failures',
                'cwe': 'CWE-798',
                'message': 'Hardcoded secret detected',
                'fix': 'Use environment variables or secure vaults'
            },
            {
                'regex': re.compile(r"execute\(.*%s|executemany\(.*%s|\.format\("),
                'severity': 'CRITICAL',
                'owasp': 'A01: Injection',
                'cwe': 'CWE-89',
                'message': 'Potential SQL injection vulnerability',
                'fix': 'Use parameterized queries instead of string formatting'
            },
            {
                'regex': re.compile(r"\beval\("),
                'severity': 'HIGH',
                'owasp': 'A01: Injection',
                'cwe': 'CWE-94',
                'message': 'Use of eval() function detected',
                'fix': 'Avoid eval(); use safer alternatives like ast.literal_eval()'
            },
            {
                'regex': re.compile(r"os\.system\(.*\+|subprocess.*shell=True"),
                'severity': 'HIGH',
                'owasp': 'A01: Injection',
                'cwe': 'CWE-78',
                'message': 'Potential command injection vulnerability',
                'fix': 'Avoid shell=True; use subprocess with list arguments'
            }
        ]

    def scan(self, file_changes: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Scan provided files for security issues.

        Args:
            file_changes: List of dictionaries containing 'file' and 'content' keys.

        Returns:
            List of detected issues with details about each vulnerability.
        """
        issues: List[Dict[str, str]] = []
        for change in file_changes:
            try:
                content = change['content']
                file_name = change['file']
                for line_num, line in enumerate(content.split('\n'), 1):
                    for rule in self.rules:
                        if rule['regex'].search(line):
                            issues.append({
                                'file': file_name,
                                'line': line_num,
                                'severity': rule['severity'],
                                'type': f"{rule['owasp']} ({rule['cwe']})",
                                'message': rule['message'],
                                'fix': rule['fix']
                            })
            except Exception:
                continue
        return issues
