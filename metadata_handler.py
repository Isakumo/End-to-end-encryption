
import datetime, json

def build_metadata(cipher="AES-GCM", key_size=256, extra=None):
    ts = datetime.datetime.utcnow().isoformat() + "Z"
    m = {
        "algorithm": cipher,
        "key_size": key_size,
        "timestamp": ts
    }
    if extra:
        m.update(extra)
    return m

def save_metadata_json(metadata: dict, path="metadata.json"):
    with open(path, "w") as f:
        json.dump(metadata, f, indent=4)
