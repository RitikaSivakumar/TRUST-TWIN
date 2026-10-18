import json
import math
import random
import time
from datetime import datetime, timezone

random.seed(42)

def generate_sample(tick):
    baseline = 85 + 2.5 * math.sin(tick / 5)
    noise = lambda: random.gauss(0, 0.7)

    a = baseline + noise()
    b = baseline + noise()
    c = baseline + noise()

    # Simulated sensor anomaly begins at sample 15.
    if tick >= 15:
        b += min((tick - 14) * 1.8, 18)

    # Simulated overheating begins at sample 30.
    if tick >= 30:
        a += min((tick - 29) * 1.4, 25)
        b += min((tick - 29) * 1.4, 25)
        c += min((tick - 29) * 1.4, 25)

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sample": tick,
        "simulated": True,
        "temperatures_c": {
            "A": round(a, 2),
            "B": round(b, 2),
            "C": round(c, 2),
        },
    }

if __name__ == "__main__":
    print("TRUST-TWIN | SIMULATED TELEMETRY PLAYBACK")
    print("Press Ctrl+C to stop.")
    tick = 0
    try:
        while True:
            tick += 1
            print(json.dumps(generate_sample(tick)), flush=True)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nPlayback stopped.")
