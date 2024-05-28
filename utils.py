import os
import json
from flask import abort

def load_json(file_path: str):
    """Load JSON data from a file."""
    with open(file_path, 'r') as file:
        return json.load(file)

def dump_json(file_path: str, data: dict):
    """Dump JSON data to a file."""
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def check_existence(path: str) -> bool:
    """Check if a path exists."""
    return os.path.exists(path)

def abort_if_not_found(condition: bool, message: str, code: int = 404):
    """Abort if a condition is not met."""
    if not condition:
        abort(code, description=message)
