import json
import os
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone


def main():
    root = ET.parse("report.xml").getroot()
    tests = []

    for case in root.iter("testcase"):
        failure = case.find("failure")
        error = case.find("error")
        problem = failure if failure is not None else error
        skipped = case.find("skipped") is not None

        if problem is not None:
            result = "failed"
            message = problem.get("message") or (problem.text or "").strip()
        elif skipped:
            result = "skipped"
            message = ""
        else:
            result = "passed"
            message = ""

        tests.append({
            "name": f'{case.get("classname", "")}::{case.get("name", "")}',
            "result": result,
            "failure_message": message
        })

    passed = sum(t["result"] == "passed" for t in tests)
    failed = sum(t["result"] == "failed" for t in tests)
    skipped = sum(t["result"] == "skipped" for t in tests)

    report = {
        "repository": os.environ.get("GITHUB_REPOSITORY", "local-run"),
        "branch": os.environ.get("GITHUB_REF_NAME", "local"),
        "commit_sha": os.environ.get("GITHUB_SHA", "local"),
        "run_id": os.environ.get("GITHUB_RUN_ID", "local"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tests": tests,
        "total": len(tests),
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "status": "failed" if failed else "passed"
    }

    receiver_url = os.environ.get("REPORT_RECEIVER_URL", "http://127.0.0.1:5001/report")
    payload = json.dumps(report).encode("utf-8")
    request = urllib.request.Request(
        receiver_url, data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        print(response.read().decode("utf-8"))
    print("Actual pytest results delivered to report receiver.")


if __name__ == "__main__":
    main()
