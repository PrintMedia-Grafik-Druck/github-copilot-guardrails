import re
from typing import List, Dict, Any


class PRScanner:
    """Parse PR diffs and extract added lines"""
    
    def scan_pr(self, diff: str) -> List[Dict[str, Any]]:
        """
        Parse unified diff and extract added lines
        
        Args:
            diff: Unified diff string from GitHub API
            
        Returns:
            List of dicts with filename, line_number, and content
        """
        added_lines = []
        current_file = None
        line_number = 0
        
        for line in diff.split('\n'):
            # Detect file header
            if line.startswith('diff --git'):
                current_file = None
            elif line.startswith('+++'):
                # Extract filename (remove +++ b/ prefix)
                match = re.match(r'\+\+\+ b/(.+)', line)
                if match:
                    current_file = match.group(1)
                    line_number = 0
            elif line.startswith('@@'):
                # Parse hunk header to get starting line number
                match = re.match(r'@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@', line)
                if match:
                    line_number = int(match.group(1))
            elif line.startswith('+') and not line.startswith('+++'):
                # This is an added line
                if current_file:
                    added_lines.append({
                        'filename': current_file,
                        'line_number': line_number,
                        'content': line[1:]  # Remove leading '+'
                    })
                line_number += 1
            elif not line.startswith('-'):
                # Context line or empty line
                line_number += 1
        
        return added_lines
