import json

MAX_FILE_SIZE_MB = 10 
MAX_ENTRIES_PER_ENTITY = 10000

def load_json_data(file_storage):
    file_storage.seek(0, 2)
    file_size = file_storage.tell()
    file_storage.seek(0)
    if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise ValueError(f"Archivo demasiado grande (>{MAX_FILE_SIZE_MB}MB)")

    try:
        content = file_storage.read().decode('utf-8')  
    except UnicodeDecodeError:
        raise ValueError("El archivo no está codificado en UTF-8.")

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        raise ValueError("El archivo no tiene formato JSON válido.")

    if not isinstance(data, dict):
        raise ValueError("El archivo debe contener un objeto JSON (no una lista ni texto plano).")

    for key, value in data.items():
        if isinstance(value, list) and len(value) > MAX_ENTRIES_PER_ENTITY:
            raise ValueError(f"Demasiados registros en '{key}'. Límite: {MAX_ENTRIES_PER_ENTITY}")

    return data
