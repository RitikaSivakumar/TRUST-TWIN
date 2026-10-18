# TRUST-TWIN: Commands and Setup Guide

## Project Overview
TRUST-TWIN is a sensor reliability prototype that analyzes simulated
engine temperature readings, evaluates sensor trust, identifies
suspicious readings, and predicts fault categories.

Platform: IBM LinuxONE Community Cloud
Operating system: Ubuntu 24.04
Architecture: s390x
Backend: Python and FastAPI
Server: Uvicorn

## 1. Connect to LinuxONE
Run from Windows PowerShell:

    ssh -i "$env:USERPROFILE\Desktop\IBM\ritikakey.pem" linux1@148.100.77.142

SSH securely connects to the remote Linux server using the private key.
Never upload the private key to GitHub.

## 2. Navigate to the Project

    cd ~/projects/trust-twin

The cd command changes the current directory to the project folder.

## 3. Activate the Python Environment

    source .venv/bin/activate

This activates the project's isolated Python environment.

## 4. Install Dependencies

    python -m pip install fastapi uvicorn numpy pandas

FastAPI provides the API framework, Uvicorn runs the server, NumPy
supports numerical operations, and Pandas supports tabular data processing
where used by the application.

## 5. Start the Backend

    python -m uvicorn app:app --host 127.0.0.1 --port 8000

This runs the FastAPI application defined by app.py on local port 8000.
Keep the terminal running while testing the application.

## 6. Create an SSH Tunnel
Run in a separate Windows PowerShell window:

    ssh -i "$env:USERPROFILE\Desktop\IBM\ritikakey.pem" -N -L 8000:127.0.0.1:8000 linux1@148.100.77.142

This forwards local port 8000 to the LinuxONE application without
exposing the application port publicly.

## 7. Open and Test the Application

    http://localhost:8000

Open this address in a browser while the SSH tunnel is running.

The application health endpoint is:

    http://localhost:8000/api/health

The logs show that the project also responds to these API routes:

    /api/analyze
    /api/ml-predict
    /api/telemetry/next

Use the application's supported parameters when testing each endpoint.

## 8. Git Setup and Verification

    git init -b main
    git remote -v
    git status

Git initializes version control, remote -v displays configured remotes,
and status shows tracked and untracked changes.

## 9. Python Dependencies

    python -m pip freeze > requirements.txt

This records installed Python packages for reproducibility.
Review the resulting file to ensure it contains the project's dependencies.

## 10. Commit and Push

    git add COMMANDS_AND_SETUP.md .gitignore requirements.txt
    git status
    git diff --cached --name-only
    git commit -m "docs: document TRUST-TWIN setup and commands"
    git push -u origin main

Review staged files before committing. Do not commit private keys,
passwords, access tokens, virtual environments, or unnecessary backups.

## 11. Verify the Commit

    git status
    git log -1 --oneline

These commands verify the working tree and show the latest commit.

## Important Notes
This project uses simulated sensor data. The prototype has not been
validated on a real vehicle. Keep this documentation updated when the
project code, dependencies, or deployment process changes.
