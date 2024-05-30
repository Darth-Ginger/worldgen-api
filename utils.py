import os
import json
from flask import abort, current_app, jsonify
import db


#region JSON/File Functions

def load_json(file_path: str):
    """Load JSON data from a file."""
    with open(file_path, 'r') as file:
        return json.load(file)

def name_to_json(name: str) -> str:
    if  not name.endswith('.json'):
        name += '.json'
    return name
def dump_json(filepath: str, data: dict):
    filepath = name_to_json(filepath)
    with open(filepath, 'w') as file:
        json.dump(data, file, indent=current_app.config['JSON_INDENT'])
def patch_dict(original: dict, patch: dict) -> dict:
    for key, value in patch.items():
        if isinstance(value, dict):
            original[key] = patch_dict(original.get(key, {}), value)
        else:
            original[key] = value
    return original

#endregion JSON/File Functions

#region World Functions

def worlds(from_file: bool=False) -> list:
    if from_file:
        return os.listdir(current_app.config['WORLDS_DIR'])
    return [world["WorldName"] for world in db.collections['Worlds'].find()]
    
def world_exists(world_name: str, from_file: bool=False) -> bool:
    if from_file and world_name in worlds():
        return True
    return not from_file and world_name in worlds()

def world_path(world_name: str) -> str:
    if world_exists(world_name):
        return os.path.join(current_app.config['WORLDS_DIR'], f"{world_name}")
    
def world_data(world_name: str, from_file: bool=False) -> dict:
    if world_exists(world_name, from_file):
        categories = world_categories(world_name)
        return {
            category.replace('.json', ''): category_data(world_name, category) 
            for category in categories
        }
def dump_world_data(world_name: str, data: dict):
    if world_exists(world_name):
        dump_json(world_path(world_name), data)
                
#endregion World Functions

#region Category Functions

def category_exists(world_name: str, category_name: str, from_file: bool=False) -> bool:
    return world_exists(world_name, from_file) and \
        (os.path.exists(f"{world_path(world_name)}/{name_to_json(category_name)}") or \
            category_name in world_categories(world_name, from_file))
     
def world_categories(world_name: str, from_file: bool=False) -> list:
    if world_exists(world_name):
        if from_file:
            return [category for category in os.listdir(world_path(world_name)) if category.endswith('.json')]
        return list(db.collections.keys())
        
def category_data(world_name: str, category_name: str, from_file: bool=False) -> dict:
    if world_exists(world_name, from_file) and category_exists(world_name, category_name, from_file):
        if from_file:
            return load_json(f"{world_path(world_name)}/{name_to_json(category_name)}")
        data = db.collections["Worlds"].find_one("WorldName", world_name)[category_name]
        return jsonify(data)
    

def dump_category_data(world_name: str, category_name: str, data: dict, to_file: bool=False):
    if world_exists(world_name, to_file) and category_exists(world_name, category_name, to_file):
        if to_file:
            dump_json(world_path(world_name), data)
        else:
            cat_data = category_data(world_name, category_name, to_file)
            data = patch_dict(cat_data, data)
            #@TODO: figure out how to patch the data in the database or add new id to the worlds collection
            
        
def dump_new_category_data(world_name: str, category_name: str, data: dict):
    if world_exists(world_name) and not category_exists(world_name, category_name, False):
        dump_json(world_path(world_name), data)
    else:
        abort(504, "Unable to create new category")


