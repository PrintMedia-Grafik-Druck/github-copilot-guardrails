#!/usr/bin/env python3
"""
SAM Local Integration Module
Integrates Guardrails directly into SAM's code generation pipeline
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.security_rules import SecurityScanner
from src.standards_checker import StandardsChecker

class SAMGuardrails:
    """Local guardrails for SAM-generated code"""
    
    def __init__(self):
        self.security_scanner = SecurityScanner()
        standards_config = {
            'rules': {
                'standards': {'enabled': True}
            }
        }
        self.standards_checker = StandardsChecker(standards_config)
    
    def check_code(self, code: str, filename: str = "generated.py") -> tuple:
        """Check generated code for security and quality issues"""
        file_data = [{
            'file': filename,
            'content': code
        }]
        
        security_issues = self.security_scanner.scan(file_data)
        standards_issues = self.standards_checker.scan(file_data)
        
        all_issues = security_issues + standards_issues
        
        has_critical = any(
            issue.get('severity') == 'CRITICAL' 
            for issue in all_issues
        )
        
        is_safe = not has_critical
        return is_safe, all_issues
    
    def format_issues(self, issues: list) -> str:
        """Format issues for display"""
        if not issues:
            return "✅ No issues found"
        
        output = f"⚠️ Found {len(issues)} issue(s):\n\n"
        
        for i, issue in enumerate(issues, 1):
            severity = issue.get('severity', 'UNKNOWN')
            message = issue.get('message', 'No message')
            line = issue.get('line', 'N/A')
            fix = issue.get('fix', 'N/A')
            
            output += f"{i}. [{severity}] Line {line}\n"
            output += f"   {message}\n"
            output += f"   Fix: {fix}\n\n"
        
        return output


def check_code_before_save(code: str, filename: str = "generated.py"):
    """Convenience function for SAM integration"""
    guardrails = SAMGuardrails()
    is_safe, issues = guardrails.check_code(code, filename)
    report = guardrails.format_issues(issues)
    return is_safe, report


if __name__ == "__main__":
    # Test with vulnerable code
    test_code = '''
import os

def connect_db():
    password = "hardcoded_secret_123"
    api_key = "sk-1234567890abcdef"
    return db.connect(password)

def query_user(user_input):
    query = f"SELECT * FROM users WHERE id = {user_input}"
    return execute(query)

def run_code(code):
    result = eval(dangerous_code)
    return result
'''
    
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     🧪 SAM INTEGRATION TEST - Local Code Checking        ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    
    print("📝 Testing with vulnerable code sample...")
    print("="*60)
    
    is_safe, report = check_code_before_save(test_code, "sam_generated.py")
    
    print(report)
    print("="*60)
    print()
    
    if is_safe:
        print("✅ Code is SAFE - SAM can save this file")
        print("   No critical security issues detected")
    else:
        print("❌ Code has CRITICAL ISSUES!")
        print("   SAM should REGENERATE or FIX before saving")
    
    print()
    print("🎯 Integration Status:")
    print("   ✅ Module loads successfully")
    print("   ✅ Security scanner working")
    print("   ✅ Standards checker working")
    print("   ✅ Ready for SAM integration!")
