class PolicyEngine:
    """Policy engine for GitHub Copilot Guardrails.
    
    Applies specified policy mode to filter issues and determine merge blocking.
    """

    def __init__(self, config: dict):
        """Initialize PolicyEngine with configuration.

        Args:
            config (dict): Configuration dictionary. Expected key 'mode' with
                one of 'ADVISORY', 'WARNING', 'BLOCKING'. Defaults to 'WARNING'.

        Raises:
            ValueError: If 'mode' is invalid.
        """
        self.mode = config.get('mode', 'WARNING')
        valid_modes = {'ADVISORY', 'WARNING', 'BLOCKING'}
        if self.mode not in valid_modes:
            raise ValueError(f"Invalid policy mode: {self.mode}")

    def apply_policy(self, issues: list) -> dict:
        """Apply policy to given issues and determine actions.

        Args:
            issues (list): List of issues, each a dict with 'severity' key.

        Returns:
            dict: Actions dict with keys 'post_comment', 'block_merge', 'filtered_issues'.

        Raises:
            TypeError: If issues is not a list or contains non-dict items.
            ValueError: If any issue lacks 'severity' key.
        """
        if not isinstance(issues, list):
            raise TypeError("issues must be a list")
        
        for idx, issue in enumerate(issues):
            if not isinstance(issue, dict):
                raise TypeError(f"Issue at index {idx} is not a dictionary")
            if 'severity' not in issue:
                raise ValueError(f"Issue at index {idx} missing 'severity' key")

        filtered_issues = []
        if self.mode == 'ADVISORY':
            filtered_issues = list(issues)
        elif self.mode == 'WARNING':
            filtered_issues = [issue for issue in issues if issue['severity'] in {'CRITICAL', 'HIGH'}]
        elif self.mode == 'BLOCKING':
            filtered_issues = list(issues)
        else:
            raise RuntimeError(f"Invalid policy mode: {self.mode}")

        block_merge = False
        if self.mode == 'BLOCKING':
            block_merge = any(issue['severity'] == 'CRITICAL' for issue in filtered_issues)

        return {
            "post_comment": True,
            "block_merge": block_merge,
            "filtered_issues": filtered_issues
        }
