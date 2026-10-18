import json
import urllib.request
import urllib.error
import sys

BASE = "http://127.0.0.1:8000"

def get_json(path):
    req = urllib.request.Request(
        BASE + path,
        headers={"Accept": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=8) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status}: {path}")
        return json.loads(response.read().decode("utf-8"))

def main():
    failures = []

    print("\nTRUST-TWIN SOFTWARE SMOKE TEST")
    print("=" * 42)

    # 1. API health
    try:
        health = get_json("/api/health")
        print("[PASS] API health:", health)
    except Exception as exc:
        print("[FAIL] API health:", exc)
        print("\nStart Uvicorn before running the tests.")
        sys.exit(1)

    # 2. Simulation scenarios
    scenarios = [
        "normal",
        "sensor_spike",
        "sensor_drift",
        "sensor_frozen",
        "vehicle_overheat",
    ]

    for scenario in scenarios:
        try:
            result = get_json(
                "/api/analyze?fault=" + scenario
            )
            print(f"[PASS] {scenario}: HTTP 200")
            print("       Response fields:", ", ".join(result.keys()))
        except Exception as exc:
            failures.append(scenario)
            print(f"[FAIL] {scenario}: {exc}")

    # 3. Repeated frozen-sensor samples
    try:
        frozen_results = [
            get_json("/api/analyze?fault=sensor_frozen")
            for _ in range(4)
        ]
        last = frozen_results[-1]
        print("[INFO] Frozen-sensor final response:")
        print(json.dumps(last, indent=2)[:1800])

        if last.get("frozen_sensor_suspected") is True:
            print("[PASS] Frozen-sensor heuristic triggered by sample 4")
        else:
            print("[WARN] Sample 4 did not report frozen_sensor_suspected=true")
            print("       Inspect the response fields above.")
    except Exception as exc:
        failures.append("frozen_sensor_repeat")
        print("[FAIL] Repeated frozen-sensor test:", exc)

    # 4. ML inference
    try:
        prediction = get_json(
            "/api/ml-predict"
            "?temperature_a=85"
            "&temperature_b=86"
            "&temperature_c=84"
        )
        print("[PASS] ML inference endpoint")
        print("       Response:", json.dumps(prediction)[:1000])
    except Exception as exc:
        failures.append("ml_predict")
        print("[FAIL] ML inference:", exc)

    print("\n" + "=" * 42)
    if failures:
        print("FAILED CHECKS:", ", ".join(failures))
        sys.exit(1)

    print("All endpoint checks passed.")
    print("Review any WARN messages before the demo.")

if __name__ == "__main__":
    main()
