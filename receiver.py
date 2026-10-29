
from flask import Flask, request, jsonify
import json
import os
from datetime import datetime, timezone

app = Flask(__name__)

REPORT_FILE = os.path.join(os.path.dirname(__file__), "test-report.json")
REPORT_TOKEN = os.environ.get("REPORT_TOKEN", "")


@app.route("/report", methods=["POST"])
def receive_report():
    if not REPORT_TOKEN or request.headers.get("X-Report-Token") != REPORT_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401

    report = request.get_json(silent=True)

    if not isinstance(report, dict):
        return jsonify({"error": "Invalid JSON report"}), 400

    report["received_at"] = datetime.now(timezone.utc).isoformat()

    with open(REPORT_FILE, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    return jsonify({
        "message": "Report saved successfully",
        "file": "test-report.json"
    }), 200


@app.route("/", methods=["GET"])
def health():
    return "Test report receiver is running."


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)
