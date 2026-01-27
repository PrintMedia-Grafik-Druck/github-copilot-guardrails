import re
from typing import List, Dict, Any

class LicenseChecker:
    """Scans repository files for license and copyright violations."""
    
    def __init__(self, github_api: Any) -> None:
        self.github_api = github_api
        
    def scan(self) -> List[Dict[str, Any]]:
        """Scan files for license and copyright issues.
        
        Returns:
            List of issues found, each with file, line, severity, type, message, and fix.
        """
        if not self.github_api.config.get('license_check_enabled', False):
            return []
        
        issues = []
        try:
            files = self.github_api.get_files()
        except Exception:
            return []
        
        try:
            proprietary = self.github_api.is_proprietary()
        except Exception:
            proprietary = False
        
        restricted_re = re.compile(r'(GPL|AGPL|LGPL)-?\d?\.?\d?')
        copyright_re = re.compile(r'Copyright \(c\) \d{4}')
        
        for file in files:
            try:
                content = self.github_api.get_file_content(file)
            except Exception:
                continue
            
            lines = content.split('\n')
            has_copyright = False
            
            for line_num, line in enumerate(lines, 1):
                license_match = restricted_re.search(line)
                if license_match:
                    license_type = license_match.group(1)
                    issues.append({
                        'file': file,
                        'line': line_num,
                        'severity': 'HIGH',
                        'type': 'restricted_license',
                        'message': f"Found restricted license '{license_match.group(0)}'",
                        'fix': 'Replace with MIT, Apache/BSD'
                    })
                    if license_type == 'GPL' and proprietary:
                        issues.append({
                            'file': file,
                            'line': line_num,
                            'severity': 'HIGH',
                            'type': 'license_conflict',
                            'message': 'GPL in proprietary project',
                            'fix': 'Remove GPL or change project license'
                        })
                if copyright_re.search(line):
                    has_copyright = True
            
            if not has_copyright:
                issues.append({
                    'file': file,
                    'line': 0,
                    'severity': 'MEDIUM',
                    'type': 'missing_copyright',
                    'message': 'Missing copyright header',
                    'fix': "Add 'Copyright (c) <year> <owner>'"
                })
        
        return issues
