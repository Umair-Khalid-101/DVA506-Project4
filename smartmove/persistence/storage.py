import json

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def load_json(path):
    with open(path) as f:
        return json.load(f)
