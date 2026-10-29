from flask import Flask, request, jsonify
import json
import os
from datetime import datetime, timezone

app = Flask(__name__)
REPORT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test-report.json")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "receiver-ready"}), 200


@app.route("/report", methods=["POST"])
def receive_report():
    report = request.get_json(silent=True)
    if not isinstance(report, dict):
        return jsonify({"error": "A JSON report is required"}), 400

    required = [
        "repository", "branch", "commit_sha", "run_id",
        "timestamp", "tests", "total", "passed", "failed", "status"
    ]
    missing = [key for key in required if key not in report]
    if missing:
        return jsonify({"error": "Missing fields", "fields": missing}), 400
    if not isinstance(report["tests"], list):
        return jsonify({"error": "tests must be a list"}), 400

    report["received_at"] = datetime.now(timezone.utc).isoformat()
    with open(REPORT_FILE, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)
    return jsonify({"message": "Report saved", "file": REPORT_FILE}), 200


if __name__ == "__main__":
    # On a self-hosted runner on this same PC, 127.0.0.1 works.
    app.run(host="127.0.0.1", port=5001, debug=False)
