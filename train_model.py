import json
from pathlib import Path
import numpy as np

rng = np.random.default_rng(42)

# Features: A, B, C temperatures, spread, mean temperature.
# Classes: normal, sensor fault, vehicle anomaly, disagreement.
def generate(n):
    X, y = [], []

    for _ in range(n):
        base = rng.normal(85, 5)
        kind = rng.choice(4, p=[.45, .25, .20, .10])
        v = base + rng.normal(0, 1.2, 3)

        if kind == 1:
            v[rng.integers(3)] += rng.choice([-1, 1]) * rng.uniform(15, 35)
        elif kind == 2:
            v += rng.uniform(20, 35)
        elif kind == 3:
            v = base + np.array([
                rng.uniform(-20, -12),
                rng.uniform(-2, 2),
                rng.uniform(12, 20)
            ])

        X.append([*v, np.ptp(v), np.mean(v)])
        y.append(kind)

    return np.array(X), np.array(y)

X, y = generate(6000)
order = rng.permutation(len(y))
split = int(.75 * len(y))
train, test = order[:split], order[split:]

# Standardize features using training data only.
mu, sd = X[train].mean(axis=0), X[train].std(axis=0) + 1e-8
A = (X[train] - mu) / sd
B = (X[test] - mu) / sd

# Train a four-class softmax classifier using NumPy gradient descent.
Y = np.eye(4)[y[train]]
W = np.zeros((5, 4))
b = np.zeros(4)
lr = 0.08

for epoch in range(500):
    logits = np.clip(A @ W + b, -30, 30)
    probs = np.exp(logits - logits.max(axis=1, keepdims=True))
    probs /= probs.sum(axis=1, keepdims=True)
    error = (probs - Y) / len(train)
    W -= lr * (A.T @ error)
    b -= lr * error.sum(axis=0)

pred = np.argmax(B @ W + b, axis=1)
accuracy = float(np.mean(pred == y[test]))
names = ["normal", "sensor_fault", "possible_vehicle_anomaly",
         "multiple_sensor_disagreement"]

class_metrics = {}
for k, name in enumerate(names):
    tp = int(np.sum((pred == k) & (y[test] == k)))
    fp = int(np.sum((pred == k) & (y[test] != k)))
    fn = int(np.sum((pred != k) & (y[test] == k)))
    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0
    class_metrics[name] = {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4)
    }

Path("models").mkdir(exist_ok=True)
np.savez("models/trust_twin_model.npz", W=W, b=b, mean=mu, std=sd)

metrics = {
    "model": "NumPy softmax classifier",
    "architecture": __import__("platform").machine(),
    "training_samples": len(train),
    "test_samples": len(test),
    "accuracy": round(accuracy, 4),
    "classes": class_metrics,
    "data_note": "Synthetic scenarios only; not validated on real vehicle telemetry."
}
Path("models/metrics.json").write_text(json.dumps(metrics, indent=2))

print("Training complete")
print("Test accuracy:", metrics["accuracy"])
print(json.dumps(class_metrics, indent=2))
print("Model: models/trust_twin_model.npz")
print("Metrics: models/metrics.json")
