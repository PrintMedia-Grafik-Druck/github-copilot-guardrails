from fastapi import FastAPI, Request, BackgroundTasks, HTTPException, status
from fastapi.responses import JSONResponse
from src.github_api import GitHubAPI
from src.scanner import PRScanner
from src.security_rules import SecurityScanner
from src.standards_checker import StandardsChecker
from src.license_checker import LicenseChecker
from src.policy_engine import PolicyEngine
from src.audit_logger import AuditLogger
from src.config_loader import ConfigLoader

app = FastAPI(title="GitHub Copilot Guardrails")

config = ConfigLoader().load_config("config.yml")
github_api = GitHubAPI(config["github"]["token"], config["github"]["repo"])
audit_logger = AuditLogger()


@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    """Handle GitHub webhook events for pull requests"""
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON")

    action = payload.get("action")
    if action not in ("opened", "synchronize", "reopened"):
        return JSONResponse({"status": "ignored", "reason": f"action={action}"})

    pr = payload.get("pull_request")
    if not pr:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing pull_request")

    pr_number = pr.get("number")
    commit_sha = pr.get("head", {}).get("sha")

    if not pr_number or not commit_sha:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing PR number or commit SHA")

    background_tasks.add_task(process_pr, pr_number, commit_sha)
    return JSONResponse({"status": "processing", "pr_number": pr_number})


def process_pr(pr_number: int, commit_sha: str):
    """Background task to scan PR and apply policy"""
    try:
        diff = github_api.get_pr_diff(pr_number)
        scanner = PRScanner()
        added_lines = scanner.scan_pr(diff)

        findings = []

        if config["security"]["enabled"]:
            sec_scanner = SecurityScanner()
            findings.extend(sec_scanner.scan(added_lines))

        if config["standards"]["enabled"]:
            std_checker = StandardsChecker()
            findings.extend(std_checker.check(added_lines))

        if config["license"]["enabled"]:
            lic_checker = LicenseChecker()
            findings.extend(lic_checker.check(added_lines))

        policy = PolicyEngine(config["policy"]["mode"])
        action = policy.evaluate(findings)

        if findings:
            comment = policy.format_comment(findings)
            github_api.post_pr_comment(pr_number, comment)

        if action == "BLOCKED":
            github_api.post_commit_status(commit_sha, "failure", "Guardrails: Critical issues found")
        elif action == "WARNED":
            github_api.post_commit_status(commit_sha, "success", "Guardrails: Warnings found")
        else:
            github_api.post_commit_status(commit_sha, "success", "Guardrails: No issues")

        audit_logger.log_scan(str(pr_number), commit_sha, findings, action)

    except Exception as e:
        print(f"Error processing PR {pr_number}: {e}")
        github_api.post_commit_status(commit_sha, "error", f"Guardrails error: {str(e)}")
