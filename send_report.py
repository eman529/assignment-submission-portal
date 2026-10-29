
import os
import json
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timezone


def main():
    xml_file = "test-results.xml"
    receiver_url = os.environ.get("REPORT_RECEIVER_URL", "").rstrip("/")
    token = os.environ.get("REPORT_TOKEN", "")

    if not receiver_url or not token:
        raise RuntimeError("REPORT_RECEIVER_URL and REPORT_TOKEN must be configured.")

    if not os.path.exists(xml_file):
        raise FileNotFoundError("test-results.xml was not generated.")

    root = ET.parse(xml_file).getroot()
    test_cases = root.findall(".//testcase")
    results = []

    for case in test_cases:
        failure = case.find("failure")
        error = case.find("error")
        skipped = case.find("skipped")

        problem = failure if failure is not None else error

        if problem is not None:
            status = "failed"
            message = problem.get("message") or (problem.text or "").strip()
        elif skipped is not None:
            status = "skipped"
            message = skipped.get("message") or (skipped.text or "").strip()
        else:
            status = "passed"
            message = None

        results.append({
            "name": case.get("classname", "") + "::" + case.get("name", ""),
            "result": status,
            "failure_message": message
        })

    total = len(results)
    passed = sum(item["result"] == "passed" for item in results)
    failed = sum(item["result"] == "failed" for item in results)
    skipped_count = sum(item["result"] == "skipped" for item in results)

    report = {
        "repository": os.environ.get("GITHUB_REPOSITORY", "local"),
        "branch": os.environ.get("GITHUB_REF_NAME", "local"),
        "commit_sha": os.environ.get("GITHUB_SHA", "local"),
        "pipeline_run_id": os.environ.get("GITHUB_RUN_ID", "local"),
        "execution_timestamp": datetime.now(timezone.utc).isoformat(),
        "total_tests": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped_count,
        "overall_status": "failed" if failed else (
            "passed" if total > 0 and skipped_count == 0 else "incomplete"
        ),
        "tests": results
    }

    data = json.dumps(report).encode("utf-8")
    request = urllib.request.Request(
        receiver_url + "/report",
        data=data,
        headers={
            "Content-Type": "application/json",
            "X-Report-Token": token
        },
        method="POST"
    )

    with urllib.request.urlopen(request, timeout=20) as response:
        print(response.read().decode("utf-8"))

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
