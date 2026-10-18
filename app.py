from pathlib import Path

import numpy as np
from collections import deque
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="TRUST-TWIN API")

BASE = Path(__file__).resolve().parent
STATIC = BASE / "static"

# Recent simulated samples used for temporal reliability checks.
SENSOR_HISTORY = deque(maxlen=8)
FROZEN_B_VALUE = 85.0

app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/")
def home():
    return FileResponse(STATIC / "index.html")


@app.get("/api/health")
def health():
    return {
        "application": "TRUST-TWIN",
        "status": "online",
        "platform": "IBM LinuxONE",
        "architecture": "s390x",
    }


@app.get("/api/analyze")
def analyze(fault: str = "none"):
    # Synthetic telemetry only. No live vehicle sensors are connected.
    rng = np.random.default_rng()
    baseline = 85.0 + rng.normal(0, 0.8)
    values = baseline + rng.normal(0, 1.0, 3)

    readings = {
        "Engine Temperature A": round(float(values[0]), 2),
        "Engine Temperature B": round(float(values[1]), 2),
        "Engine Temperature C": round(float(values[2]), 2),
    }

    if fault == "sensor_b":
        readings["Engine Temperature B"] += 25
    elif fault == "all_disagree":
        readings.update({
            "Engine Temperature A": 70.0,
            "Engine Temperature B": 100.0,
            "Engine Temperature C": 85.0,
        })
    elif fault == "vehicle_overheat":
        readings.update({
            "Engine Temperature A": 112.0,
            "Engine Temperature B": 110.5,
            "Engine Temperature C": 111.2,
        })
    elif fault == "sensor_spike":
        readings["Engine Temperature B"] += 38
    elif fault == "sensor_drift":
        readings["Engine Temperature B"] += 12
    elif fault == "sensor_frozen":
        # Channel B remains fixed while A and C vary on successive requests.
        readings["Engine Temperature A"] = round(float(91.0 + rng.normal(0, 1.2)), 2)
        readings["Engine Temperature B"] = FROZEN_B_VALUE
        readings["Engine Temperature C"] = round(float(89.0 + rng.normal(0, 1.2)), 2)

    # Track recent readings for the selected scenario.
    sample = {
        "scenario": fault,
        "readings": dict(readings),
    }
    if fault == "sensor_frozen":
        SENSOR_HISTORY.append(sample)
    else:
        # Avoid mixing an old frozen-sensor test with unrelated scenarios.
        SENSOR_HISTORY.clear()

    frozen_detected = False
    if fault == "sensor_frozen" and len(SENSOR_HISTORY) >= 4:
        b_values = [
            item["readings"]["Engine Temperature B"]
            for item in SENSOR_HISTORY
        ]
        a_values = [
            item["readings"]["Engine Temperature A"]
            for item in SENSOR_HISTORY
        ]
        c_values = [
            item["readings"]["Engine Temperature C"]
            for item in SENSOR_HISTORY
        ]
        b_stable = max(b_values) - min(b_values) < 0.05
        other_channels_move = (
            max(a_values) - min(a_values) >= 1.0
            or max(c_values) - min(c_values) >= 1.0
        )
        frozen_detected = b_stable and other_channels_move

    names = list(readings)
    values = np.array(list(readings.values()), dtype=float)
    median = float(np.median(values))
    deviations = np.abs(values - median)

    trust = {
        name: round(float(100 * np.exp(-deviation / 5)), 1)
        for name, deviation in zip(names, deviations)
    }
    flagged = [
        name for name, deviation in zip(names, deviations)
        if deviation > 8
    ]

    if fault == "vehicle_overheat" or (
        float(np.median(values)) >= 105
    ):
        status = "POSSIBLE VEHICLE ANOMALY"
        explanation = (
            "All readings indicate elevated temperature. Verify with an "
            "independent reference; this simulated assessment is not a "
            "safety-certified diagnosis."
        )
    elif frozen_detected:
        if "Engine Temperature B" not in flagged:
            flagged.append("Engine Temperature B")
        status = "FROZEN SENSOR SUSPECTED"
        explanation = (
            "Channel B remained unchanged across consecutive simulated samples "
            "while another channel varied. This is a temporal freeze heuristic, "
            "not proof of a real hardware fault."
        )
    elif len(flagged) == 1 or fault in ("sensor_spike", "sensor_drift"):
        status = "SENSOR DISAGREEMENT"
        explanation = (
            f"{flagged[0] if flagged else 'A sensor'} may be abnormal. "
            "This is a simulated assessment; inspect the trend and verify independently."
        )
    elif fault == "sensor_frozen":
        status = "MONITORING FOR FROZEN SENSOR"
        explanation = (
            f"Consecutive simulated samples collected: {len(SENSOR_HISTORY)}/4. "
            "Channel B is held at a fixed value; more samples are needed to "
            "compare its stability with the other channels."
        )
    elif len(flagged) > 1:
        status = "UNCERTAIN"
        explanation = (
            "Multiple readings disagree with the median. The system cannot "
            "confidently isolate a single faulty sensor."
        )
    else:
        status = "CONSENSUS"
        explanation = (
            "No reading exceeds the disagreement threshold. Sensor agreement "
            "does not guarantee that every sensor is correct."
        )

    return {
        "simulated": True,
        "scenario": fault,
        "temporal_samples": len(SENSOR_HISTORY) if fault == "sensor_frozen" else 0,
        "frozen_sensor_suspected": frozen_detected,
        "readings": readings,
        "consensus_temperature": round(median, 2),
        "deviations_c": {
            name: round(float(dev), 2)
            for name, dev in zip(names, deviations)
        },
        "trust_scores": trust,
        "flagged_sensors": flagged,
        "status": status,
        "explanation": explanation,
    }


# TRUST-TWIN trained ML inference endpoint
from functools import lru_cache
from fastapi import HTTPException, Query

@lru_cache(maxsize=1)
def load_trust_twin_model():
    import numpy as np
    path = BASE / "models" / "trust_twin_model.npz"
    if not path.exists():
        raise FileNotFoundError("Trained model file is missing")
    with np.load(path) as data:
        return (
            data["W"].copy(),
            data["b"].copy(),
            data["mean"].copy(),
            data["std"].copy(),
        )

@app.get("/api/ml-predict")
def ml_predict(
    temperature_a: float = Query(..., ge=-50, le=250),
    temperature_b: float = Query(..., ge=-50, le=250),
    temperature_c: float = Query(..., ge=-50, le=250),
):
    import numpy as np

    try:
        W, b, mean, std = load_trust_twin_model()
    except (FileNotFoundError, OSError, ValueError) as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    values = np.array(
        [temperature_a, temperature_b, temperature_c], dtype=float
    )
    features = np.array([
        *values,
        float(np.ptp(values)),
        float(np.mean(values)),
    ])

    scaled = (features - mean) / std
    logits = np.clip(scaled @ W + b, -30, 30)
    probs = np.exp(logits - np.max(logits))
    probs /= probs.sum()

    labels = [
        "normal",
        "sensor_fault",
        "possible_vehicle_anomaly",
        "multiple_sensor_disagreement",
    ]
    best = int(np.argmax(probs))

    return {
        "model": "NumPy softmax classifier",
        "prediction": labels[best],
        "class_probabilities": {
            labels[i]: round(float(probs[i]), 4)
            for i in range(len(labels))
        },
        "temperatures": {
            "A": temperature_a,
            "B": temperature_b,
            "C": temperature_c,
        },
        "simulated_input": True,
        "data_note": (
            "Trained on synthetic scenarios. Probabilities are not "
            "calibrated safety confidence and are not validated on "
            "real vehicle telemetry."
        ),
    }


@app.get("/api/diagnostics")
def diagnostics():
    from pathlib import Path
    import platform

    root = Path(__file__).resolve().parent
    model = root / "models" / "trust_twin_model.npz"
    metrics = root / "models" / "metrics.json"

    return {
        "application": "TRUST-TWIN",
        "status": "online",
        "platform": "IBM LinuxONE",
        "architecture": platform.machine(),
        "simulation_mode": True,
        "model_file_present": model.is_file(),
        "metrics_file_present": metrics.is_file(),
        "safety_note": (
            "Synthetic-data prototype; not validated for real vehicle safety."
        ),
    }



@app.post("/api/telemetry/reset")
def telemetry_reset():
    global _PLAYBACK_TICK
    _PLAYBACK_TICK = 0
    return {
        "status": "reset",
        "sample": 0,
        "simulated": True,
        "message": "Playback sequence reset."
    }

# TRUST-TWIN simulated telemetry playback
from datetime import datetime, timezone
import math
import random

_PLAYBACK_TICK = 0

@app.get("/api/telemetry/next")
def telemetry_next():
    global _PLAYBACK_TICK
    _PLAYBACK_TICK += 1
    tick = _PLAYBACK_TICK

    baseline = 85 + 2.5 * math.sin(tick / 5)
    rng = random.Random(42 + tick)

    a = baseline + rng.gauss(0, 0.7)
    b = baseline + rng.gauss(0, 0.7)
    c = baseline + rng.gauss(0, 0.7)

    if tick >= 15:
        b += min((tick - 14) * 1.8, 18)

    if tick >= 30:
        rise = min((tick - 29) * 1.4, 25)
        a += rise
        b += rise
        c += rise

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sample": tick,
        "simulated": True,
        "temperatures_c": {
            "A": round(a, 2),
            "B": round(b, 2),
            "C": round(c, 2),
        },
        "note": "Synthetic demonstration data; not live vehicle telemetry."
    }
