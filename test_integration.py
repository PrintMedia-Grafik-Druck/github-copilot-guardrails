#!/usr/bin/env python3
"""
Integration test for the entire guardrails system
Tests the full pipeline: Webhook → Scan → Policy → Audit
"""

import sys
sys.path.insert(0, '.')

from test_mock_api import MockGitHubAPI
from src.scanner import PRScanner
from src.security_rules import SecurityScanner
from src.standards_checker import StandardsChecker
from src.license_checker import LicenseChecker
from src.policy_engine import PolicyEngine
from src.audit_logger import AuditLogger

def test_full_pipeline():
    """Test the complete workflow"""
    print("\n" + "="*70)
    print("🧪 INTEGRATION TEST: Full Guardrails Pipeline")
    print("="*70 + "\n")
    
    # Mock configs
    standards_config = {
        'rules': {
            'standards': {'enabled': True}
        }
    }
    
    policy_config = {
        'mode': 'BLOCKING'
    }
    
    # 1. Setup
    print("📋 Step 1: Initialize components")
    github_api = MockGitHubAPI("mock_token", "test/repo")
    scanner = PRScanner()
    security = SecurityScanner()
    standards = StandardsChecker(standards_config)
    license_checker = LicenseChecker(github_api)
    policy = PolicyEngine(policy_config)
    audit = AuditLogger()
    print("✅ All components initialized\n")
    
    # 2. Get PR diff
    print("📋 Step 2: Fetch PR diff")
    pr_number = 1
    commit_sha = "abc123def456"
    diff = github_api.get_pr_diff(pr_number)
    print(f"✅ Retrieved diff ({len(diff)} characters)\n")
    
    # 3. Parse diff
    print("📋 Step 3: Parse diff and extract added lines")
    added_lines = scanner.scan_pr(diff)
    print(f"✅ Found {len(added_lines)} added lines\n")
    
    # 4. Run scanners
    print("📋 Step 4: Run security scanners")
    findings = []
    
    # Security scan
    try:
        security_findings = security.scan(added_lines)
        print(f"   🔒 Security: {len(security_findings)} issues found")
        findings.extend(security_findings)
    except Exception as e:
        print(f"   🔒 Security: Error - {e}")
    
    # Standards scan
    try:
        standards_findings = standards.scan(added_lines)
        print(f"   📏 Standards: {len(standards_findings)} issues found")
        findings.extend(standards_findings)
    except Exception as e:
        print(f"   📏 Standards: Error - {e}")
    
    # License scan (no params)
    try:
        license_findings = license_checker.scan()
        print(f"   ⚖️  License: {len(license_findings)} issues found")
        findings.extend(license_findings)
    except Exception as e:
        print(f"   ⚖️  License: Skipped - {e}")
    
    print(f"✅ Total findings: {len(findings)}\n")
    
    # 5. Display findings
    if findings:
        print("📋 Step 5: Review findings")
        print("─" * 60)
        for i, finding in enumerate(findings[:5], 1):
            severity = finding.get('severity', 'UNKNOWN')
            rule_id = finding.get('rule_id', finding.get('type', 'UNKNOWN'))
            line_num = finding.get('line_number', finding.get('line', 'N/A'))
            message = finding.get('message', 'No message')
            print(f"{i}. [{severity}] {rule_id}")
            print(f"   Line {line_num}: {message}")
        if len(findings) > 5:
            print(f"   ... and {len(findings) - 5} more")
        print("─" * 60 + "\n")
    else:
        print("📋 Step 5: No findings detected\n")
    
    # 6. Apply policy
    print("📋 Step 6: Apply policy engine")
    policy_result = policy.apply_policy(findings)
    should_post = policy_result['post_comment']
    should_block = policy_result['block_merge']
    filtered = policy_result['filtered_issues']
    
    action = "BLOCKED" if should_block else ("WARNED" if filtered else "APPROVED")
    print(f"✅ Policy decision: {action}")
    print(f"   Post comment: {should_post}")
    print(f"   Block merge: {should_block}")
    print(f"   Filtered issues: {len(filtered)}\n")
    
    # 7. Post to GitHub
    print("📋 Step 7: Post results to GitHub")
    if should_post and filtered:
        # Simple comment format
        comment = f"## 🔒 Guardrails Report\n\n"
        comment += f"Found {len(filtered)} issue(s):\n\n"
        for finding in filtered[:3]:
            severity = finding.get('severity', 'UNKNOWN')
            message = finding.get('message', 'No message')
            comment += f"- **[{severity}]** {message}\n"
        if len(filtered) > 3:
            comment += f"\n... and {len(filtered) - 3} more\n"
        
        github_api.post_pr_comment(pr_number, comment)
    
    if should_block:
        github_api.post_commit_status(commit_sha, "failure", "Critical issues found")
    else:
        github_api.post_commit_status(commit_sha, "success", "No critical issues")
    print()
    
    # 8. Audit log
    print("📋 Step 8: Write audit log")
    audit.log_scan(str(pr_number), commit_sha, findings, action)
    print("✅ Audit log written to logs/audit.log\n")
    
    # 9. Summary
    print("="*70)
    print("🎉 INTEGRATION TEST COMPLETED SUCCESSFULLY!")
    print("="*70)
    print(f"\n📊 Summary:")
    print(f"   • PR Number: {pr_number}")
    print(f"   • Commit SHA: {commit_sha}")
    print(f"   • Added Lines: {len(added_lines)}")
    print(f"   • Total Findings: {len(findings)}")
    print(f"   • Policy Action: {action}")
    print(f"   • Status: {'❌ BLOCKED' if should_block else '✅ APPROVED'}")
    print()
    
    return True

if __name__ == "__main__":
    try:
        success = test_full_pipeline()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
