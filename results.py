
import datetime, json, os
from typing import Dict
import matplotlib.pyplot as plt

RESULTS_JSON = "encryption_results.json"
RESULTS_TEXT = "encryption_results.txt"
PLOT_PNG = "encryption_times.png"

def _load_all():
    if os.path.exists(RESULTS_JSON):
        with open(RESULTS_JSON, "r") as f:
            return json.load(f)
    return []

def append_metrics(metrics: Dict):
    allm = _load_all()
    metrics["_captured_at"] = datetime.datetime.utcnow().isoformat() + "Z"
    allm.append(metrics)
    with open(RESULTS_JSON, "w") as f:
        json.dump(allm, f, indent=4)
    print(f"Appended metrics to {RESULTS_JSON}")

def save_text_report(filename=RESULTS_TEXT):
    allm = _load_all()
    with open(filename, "w") as f:
        f.write("End-to-End Encryption Project - Results Report\n")
        f.write(f"Generated on: {datetime.datetime.utcnow().isoformat()}Z\n\n")
        for i, m in enumerate(allm):
            f.write(f"--- Run {i+1} ---\n")
            for k, v in m.items():
                f.write(f"{k}: {v}\n")
            f.write("\n")
    print(f"Saved human-readable report to {filename}")

def plot_times(filename=PLOT_PNG):
    allm = _load_all()
    enc = [m.get("encryption_time_ms") for m in allm if m.get("encryption_time_ms") is not None]
    dec = [m.get("decryption_time_ms") for m in allm if m.get("decryption_time_ms") is not None]
    if not enc and not dec:
        print("No timing data to plot.")
        return
    plt.figure(figsize=(6,4))
    if enc:
        plt.plot(enc, marker='o', label="encryption_time_ms")
    if dec:
        plt.plot(dec, marker='x', label="decryption_time_ms")
    plt.xlabel("Run index")
    plt.ylabel("Milliseconds")
    plt.title("Encryption/Decryption Times")
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
    print(f"Saved timing plot to {filename}")

if __name__ == "__main__":
    # quick demo: generate report and plot
    save_text_report()
    plot_times()
