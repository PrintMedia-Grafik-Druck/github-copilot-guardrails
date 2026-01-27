#!/usr/bin/env python3
"""
Test if security scanner actually detects issues
"""

import sys
sys.path.insert(0, '.')

from src.security_rules import SecurityScanner

# Test data with CORRECT format (file + content as full string)
test_files = [
    {
        'file': 'app.py',
        'content': '''import os
password = "hardcoded_secret_123"
api_key = "sk-1234567890abcdef"
def connect():
    return db.connect(password)
'''
    },
    {
        'file': 'db.py',
        'content': '''def query_user(user_input):
    query = f"SELECT * FROM users WHERE id = {user_input}"
    return execute(query)
'''
    },
    {
        'file': 'eval.py',
        'content': '''def run_code(code):
    result = eval(dangerous_code)
    return result
'''
    },
    {
        'file': 'cmd.py',
        'content': '''import subprocess
subprocess.call(user_input, shell=True)
os.system("rm -rf " + path)
'''
    }
]

print("🔍 Testing Security Scanner Detection\n")
print("="*60)

scanner = SecurityScanner()
findings = scanner.scan(test_files)

print(f"\n✅ Security Scanner found {len(findings)} issues:\n")

if findings:
    for i, finding in enumerate(findings, 1):
        print(f"{i}. [{finding.get('severity', 'UNKNOWN')}] {finding.get('type', 'UNKNOWN')}")
        print(f"   File: {finding.get('file', 'N/A')}:{finding.get('line', 'N/A')}")
        print(f"   Message: {finding.get('message', 'No message')}")
        print(f"   Fix: {finding.get('fix', 'N/A')}")
        print()
else:
    print("❌ NO ISSUES DETECTED - Scanner might be broken!")
    sys.exit(1)

print("="*60)
print(f"🎉 Security Scanner detected {len(findings)} vulnerabilities!")
