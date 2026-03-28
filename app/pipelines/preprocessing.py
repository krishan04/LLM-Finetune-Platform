import json

def prepare_dataset(file_path):

    processed_path = file_path.replace(".json", "_processed.json")

    with open(file_path, "r") as f:
        data = json.load(f)

    formatted = []

    for item in data:
        text = item.get("text") or f"{item.get('instruction', '')} {item.get('output', '')}"
        formatted.append({"text": text})

    with open(processed_path, "w") as f:
        json.dump(formatted, f)

    return processed_path
