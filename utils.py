import os
import json
from flask import abort, app

def load_json(file_path: str):
    """Load JSON data from a file."""
    with open(file_path, 'r') as file:
        return json.load(file)

def check_existence(path: str) -> bool:
    """Check if a path exists."""
    return os.path.exists(path)

def world_exists(world_name: str, abortable: bool = True) -> bool:
    if os.path.exists(os.path.join(app.config['WORLDS_DIR'], f"{world_name}")):
        return True
    if abortable:
        abort(404, "World not found")
    return False
    

def abort_if_not_found(condition: bool, message: str, code: int = 404):
    """Abort if a condition is not met."""
    if not condition:
        abort(code, description=message)
        
def name_to_json(name: str) -> str:
    if  not name.endswith('.json'):
        name += '.json'
    return name

def category_exists(world_name: str, category_name: str, abortable: bool = True) -> bool:
    name_to_json(category_name)
    if world_exists(world_name) and os.path.exists(os.path.join(world_path(world_name), f"{category_name}")):
        return True
    if abortable:
        abort(404, f"Category not found for World: {world_name}")
    return False
        
def world_path(world_name: str) -> str:
    if world_exists(world_name):
        return os.path.join(app.config['WORLDS_DIR'], f"{world_name}")

def world_categories(world_name: str) -> list:
    if world_exists(world_name):
        return [category for category in os.listdir(world_path(world_name)) if category.endswith('.json')]

def world_data(world_name: str) -> dict:
    if world_exists(world_name):
        categories = world_categories(world_name)
        return {
            category.replace('.json', ''): category_data(world_name, category) 
            for category in categories
        }

def category_data(world_name: str, category_name: str) -> dict:
    name_to_json(category_name)
    if world_exists(world_name) and category_exists(world_name, category_name):
        return load_json(os.path.join(world_path(world_name), f"{category_name}"))

def dump_json(filepath: str, data: dict):
    filepath = name_to_json(filepath)
    with open(filepath, 'w') as file:
        json.dump(data, file, indent=app.config['JSON_INDENT'])

def dump_world_data(world_name: str, data: dict):
    if world_exists(world_name):
        dump_json(world_path(world_name), data)
      
def dump_category_data(world_name: str, category_name: str, data: dict):
    if world_exists(world_name) and category_exists(world_name, category_name):
        dump_json(world_path(world_name), data)
        
def dump_new_category_data(world_name: str, category_name: str, data: dict):
    if world_exists(world_name) and not category_exists(world_name, category_name, False):
        dump_json(world_path(world_name), data)
    else:
        abort(504, "Unable to create new category")

def patch_dict(original: dict, patch: dict) -> dict:
    for key, value in patch.items():
        if isinstance(value, dict):
            original[key] = patch_dict(original.get(key, {}), value)
        else:
            original[key] = value
    return original
