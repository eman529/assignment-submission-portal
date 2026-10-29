# Assignment Submission Portal

## Project description
A Flask web portal that accepts a student's name, registration number, assignment title, and submission URL. It validates required fields and URLs, saves valid submissions in SQLite, and displays saved records.

## Requirements
- Python 3.10 or newer
- Git
- Flask and pytest (installed from requirements.txt)

## Setup on Windows PowerShell
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run the portal
```powershell
python app.py
```
Open http://127.0.0.1:5000 in your browser.

## Run tests
```powershell
python -m pytest -v
```
Generate actual JUnit results:
```powershell
python -m pytest -v --junitxml=report.xml
```

## Start the local report receiver
In a second terminal with the virtual environment activated:
```powershell
python receiver.py
```
Receiver health check: http://127.0.0.1:5001/health

Send a locally generated test report:
```powershell
python send_report.py
```
The receiver saves the received JSON to `test-report.json`.

## GitHub Actions
The workflow in `.github/workflows/ci.yml` runs on every push to `main`. To deliver reports automatically to your computer, configure a GitHub self-hosted runner on the same computer and keep both the runner and receiver running during the demonstration. A GitHub-hosted runner's localhost is not your computer's localhost.

## Required demonstration
1. Push a passing revision.
2. Introduce a temporary defect and push it; the test workflow must fail and report the failure.
3. Fix the defect and push again; the workflow must pass.
4. Show the GitHub Actions results and the automatically updated local `test-report.json`.

## Security note
Do not commit passwords, access tokens, or email credentials.
