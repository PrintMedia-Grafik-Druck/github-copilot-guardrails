"""
Mock GitHub API for testing without real GitHub token
"""

class MockGitHubAPI:
    """Simulates GitHub API responses for testing"""
    
    def __init__(self, token, repo):
        self.token = token
        self.repo = repo
        print(f"✅ Mock GitHub API initialized for {repo}")
    
    def get_pr_diff(self, pr_number):
        """Return a sample diff with security issues"""
        return """diff --git a/app.py b/app.py
index 1234567..abcdefg 100644
--- a/app.py
+++ b/app.py
@@ -10,6 +10,12 @@ import requests
 
 def connect_db():
+    password = "hardcoded_secret_123"
+    api_key = "sk-1234567890abcdef"
     conn = psycopg2.connect(
+        host="localhost",
+        user="admin",
+        password=password
     )
+    query = f"SELECT * FROM users WHERE id = {user_input}"
+    result = eval(dangerous_code)
     return conn
"""
    
    def post_pr_comment(self, pr_number, body):
        """Simulate posting a comment"""
        print(f"\n📝 Would post PR comment to #{pr_number}:")
        print("─" * 60)
        print(body)
        print("─" * 60)
        return {"id": 12345, "body": body}
    
    def post_commit_status(self, commit_sha, state, description):
        """Simulate posting commit status"""
        print(f"\n✅ Would post commit status to {commit_sha[:7]}:")
        print(f"   State: {state}")
        print(f"   Description: {description}")
        return {"state": state, "description": description}
    
    def get_file_content(self, path):
        """Simulate getting file content"""
        return "# Sample file content"
    
    def get_files(self):
        """Simulate getting repository files"""
        return ["app.py", "config.py", "test.py"]
