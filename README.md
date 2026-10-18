# TRUST-TWIN
### AI-Powered Sensor Reliability and Fault Analysis on IBM LinuxONE

TRUST-TWIN is an AI-powered sensor reliability prototype designed to analyze simulated vehicle engine telemetry, evaluate sensor trustworthiness, identify suspicious readings, and predict possible fault categories.

The project combines sensor comparison logic, trust scoring, and machine learning to help interpret conflicting sensor data and support more informed vehicle-health monitoring.

**Project status:** Working software prototype using simulated sensor data. Real-world vehicle validation has not yet been performed.

---

## Problem Statement

Vehicle monitoring systems depend on sensor readings to understand engine conditions. However, sensors may produce incorrect, inconsistent, drifting, or frozen readings.

When sensor data is unreliable, it becomes difficult to determine whether an unusual value represents a sensor fault or a possible engine abnormality.

TRUST-TWIN explores a software-based approach to evaluating sensor reliability before interpreting the data.

## Our Solution

TRUST-TWIN analyzes simulated readings from three temperature sensors, compares their values, calculates sensor trust scores, identifies suspicious readings, and uses a machine-learning model to predict fault categories.

A V6 six-cylinder engine CAD model provides the engineering context for the concept. The current software prototype uses simulated sensor data and is not physically connected to the CAD model.

## Key Features

- **Multi-sensor comparison:** Compares readings from three simulated temperature sensors.
- **Sensor trust scoring:** Estimates sensor reliability using the implemented comparison logic.
- **Fault scenario simulation:** Demonstrates supported scenarios such as sudden spikes, gradual drift, and frozen readings.
- **Temperature anomaly analysis:** Examines rising readings that may indicate possible overheating.
- **Machine-learning predictions:** Predicts fault categories using the trained model.
- **Interactive dashboard:** Displays sensor readings and analysis results.
- **Telemetry playback:** Includes a tool for telemetry playback.
- **FastAPI backend:** Provides the application's backend functionality.
- **IBM LinuxONE deployment:** Runs on IBM LinuxONE Community Cloud.

## How It Works

1. **Sensor input:** The system receives simulated temperature readings from three sensors.
2. **Sensor comparison:** It compares the readings to identify inconsistencies.
3. **Trust assessment:** It calculates trust scores to help identify suspicious sensor behaviour.
4. **Fault analysis:** Implemented logic examines sensor disagreement and possible temperature anomalies.
5. **Machine-learning analysis:** The trained model predicts fault categories from supported inputs.
6. **Dashboard output:** Results are presented through the web dashboard.

The output supports analysis and is not a replacement for engineering judgment or a validated vehicle safety system.

## System Architecture

```text
Simulated Sensor Data
          |
          v
Three Temperature Sensors
          |
          v
Sensor Comparison and Trust Scoring
          |
          v
Fault and Temperature Analysis
          |
          v
Machine-Learning Prediction
          |
          v
FastAPI Backend
          |
          v
Web Dashboard
          |
          v
Sensor Status and Analysis Results
```

This diagram represents the conceptual workflow. Refer to the application code for the exact implementation and execution order.

## Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| Backend framework | FastAPI |
| API server | Uvicorn |
| Numerical processing | NumPy |
| Frontend | HTML, CSS, JavaScript |
| Machine learning | Implemented Python model |
| Model artifacts | NumPy-compatible model file |
| Deployment platform | IBM LinuxONE Community Cloud |
| Operating system | Ubuntu 24.04 |
| Architecture | s390x |

The project's Python dependencies are listed in `requirements.txt`.

## Project Structure

```text
TRUST-TWIN/
├── app.py
├── train_model.py
├── requirements.txt
├── COMMANDS_AND_SETUP.md
├── .gitignore
├── models/
│   ├── metrics.json
│   └── trust_twin_model.npz
├── static/
│   └── index.html
├── tests/
│   └── smoke_test.py
└── tools/
    └── telemetry_playback.py
```

## Getting Started

### Prerequisites

- Python 3
- Git
- Access to the repository
- A Linux environment or compatible development environment

### 1. Clone the Repository

```bash
git clone https://github.com/RitikaSivakumar/TRUST-TWIN
