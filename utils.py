import json


from bson import ObjectId
from config import Config


#region JSON File Functions

def name_to_json(name: str) -> str:
    if  not name.endswith('.json'):
        name += '.json'
    return name

def load_json(file_path: str):
    """Load JSON data from a file."""
    file_path =name_to_json(file_path)
    with open(file_path, 'r') as file:
        return json.load(file)

def dump_json(filepath: str, data: dict):
    filepath = name_to_json(filepath)
    with open(filepath, 'w') as file:
        json.dump(data, file, indent=Config.JSON_INDENT)

#endregion JSON File Functions

#region Dict Functions

def patch_dict(original: dict, patch: dict) -> dict:
    for key, value in patch.items():
        if isinstance(value, dict):
            original[key] = patch_dict(original.get(key, {}), value)
        else:
            original[key] = value
    return original

#endregion Dict Functions

#region Conversion Functions

def serialize_doc(doc: dict) -> dict:
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            doc[key] = str(value)
    return doc

#endregion Conversion Functions




