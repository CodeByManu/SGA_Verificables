import json

def load_json_data(file_storage):
    content = file_storage.read()
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        raise ValueError("El archivo no tiene formato JSON válido.")
    return data
