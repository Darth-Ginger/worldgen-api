import os
import json
import re
from typing import Union
from apiflask import abort
from flask import current_app, jsonify
import db
from pymongo import collection
from pymongo.results import UpdateResult 
from bson import ObjectId


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

def upsert_object(collection: collection, obj: dict) -> Union[ObjectId, None]:
    """
    Insert or update an object in the specified collection.

    :param collection: The MongoDB collection.
    :param obj: The object to insert or update.
    :return: The _id of the inserted or updated object.
    """
    if '_id' in obj and obj['_id']:
        obj_id = obj['_id']
        del obj['_id']
        result = collection.update_one({'_id': ObjectId(obj_id)}, {'$set': obj}, upsert=True)
        if result.upserted_id is not None:
            return result.upserted_id
        else:
            return ObjectId(obj_id)
    else:
        result = collection.insert_one(obj)
        return result.inserted_id
    
def to_ObjectId(obj: Union[ObjectId, str]) -> Union[ObjectId, None]:
    objectid_pattern = re.compile(r'^[0-9a-fA-F]{24}$')
    if isinstance(obj, ObjectId):
        return obj
    elif re.match(objectid_pattern, obj):
        return ObjectId(obj)
    else:
        world = db.collections["Worlds"].find_one({"WorldName": obj})
        if world is not None:
            return world["_id"]
        return None

def is_iterable(var: object) -> bool:
    try:
        _ = iter(var)
        return True
    except TypeError:
        return False
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
    """
    Retrieves the data for a given world.

    Args:
        world_name (str): The name of the world to retrieve the data for.
        from_file (bool, optional): Whether to retrieve the data from a file or from the database. Defaults to False.

    Returns:
        dict: A dictionary containing the data of the specified world.

    Raises:
        None

    Description:
        This function retrieves the data for a given world. It first checks if the world exists using the `world_exists` function. If the world exists, it checks if the data should be retrieved from a file or from the database. If the data should be retrieved from a file, it loads the data from a JSON file using the `load_json` function. If the data should be retrieved from the database, it retrieves the data from the "Worlds" collection in the database using the `find_one` method. It then iterates over the categories in the world data and retrieves the corresponding category data using the `category_data_by_id` function. Finally, it replaces the category IDs in the world data with the full category data and returns the world data.
    """
    if from_file:
        return load_json(f"{world_path(world_name)}/{name_to_json(world_name)}")
    
    world = db.collections["Worlds"].find_one({"WorldName": world_name})
    for category in world.keys():
        if is_iterable(world[category]):
            if isinstance(world[category], dict):
                full_category = category_data_by_id(world[category])
            elif isinstance(world[category], list):
                full_category = [category_data_by_id(item) for item in world[category]]
            else:
                raise ValueError("Invalid type for category: {}".format(type(world[category])))
        else:
            full_category = category_data_by_id(world[category])
        world[category] = full_category
            
    return world

def build_world_data(obj_id: Union[ObjectId, str], data: Union[dict, str, ObjectId, list]) -> object:
    obj_id = to_ObjectId(obj_id)
    
    #@TODO Rework to recursively build a world json object
    
                
def dump_world_data(world_name: str, data: dict):
    if world_exists(world_name):
        for category in data.values():
            dump_category_data(world_name, category)
    
def update_world_reference(world_id: Union[ObjectId, str], update_fields: dict) -> UpdateResult:   
    """_summary_

    Args:
        world_id (Union[ObjectId, str]): _description_
        update_fields (dict): _description_

    Returns:
        UpdateResult: Includes the number of documents matched, modified, and upserted.
        
    Example:
        >>> update_fields = {
            Geography: {
                "Landmarks": {
                    "The Sky Needle": "A thin, incredibly tall, mountain that is home to a dragon"
                }
            },
            "Leaders": {
                "name": "Antonius Whitehearth",
                "kingdom": "Elanthia",
                "traits": ["Influential", "Intelligent", "Pious"],
                "goals": ["Decipher the laws of the cosmos", "Discover how to become a God"],
                "short_name": "AW",
                "relationships": [
                    "reputation": 80,
                    "from": "Antonius Whitehearth",
                    "to": "High Councilor Thalindra",
                    "name": "AW-HC",
                    "intelligence": {
                        "level": "High",
                        "schemes": ["Expand mithril trade", "Strengthen economic ties"],
                        "known_schemes": [
                            "Elanthia's magical advancements"
                        ]
                ]
        }
        >>> update_world_reference("world1", update_fields)
        >>> update_world_reference("60c72b2f9af1c88a4a4c6a5b", update_fields)
    """
    if world_exists(world_id, False):
        world_id = db.collections["Worlds"].find_one({"WorldName": world_id})["_id"]
        
    world_id = to_ObjectId(world_id)
        
    update_data = {}
    for field, value in update_fields.items():
        if field in db.collections:
            if isinstance(value, list):
                update_ids = [upsert_object(db.collections[field], obj) for obj in value]
                update_data[field] = update_ids
            else:
                updated_id = upsert_object(db.collections[field], value)
                update_data[field] = updated_id
        else:
            update_data[field] = value
            
    result = db.collections["Worlds"].update_one({"_id": world_id}, {"$set": update_data})    
    
    return result

#endregion World Functions

#region Category Functions

def category_exists(world_name: str, category_name: str, from_file: bool=False) -> bool:
    return world_exists(world_name, from_file) and \
        (os.path.exists(f"{world_path(world_name)}/{name_to_json(category_name)}") or \
            category_name in world_categories(world_name, from_file))

def world_categories(world_name: str, from_file: bool=False) -> list:
    if world_exists(world_name, from_file):
        if from_file:
            return [category for category in os.listdir(world_path(world_name)) if category.endswith('.json')]
        return list(db.collections.keys())

def category_data(world_name: str, category_name: str, from_file: bool=False) -> dict:
    if world_exists(world_name, from_file) and category_exists(world_name, category_name, from_file):
        if from_file:
            return load_json(f"{world_path(world_name)}/{name_to_json(category_name)}")
        else:
            data_ids = db.collections["Worlds"].find_one("WorldName", world_name)[category_name]
            data = db.collections[category_name].find({"_id": {"$in": data_ids}})
            return jsonify(data)
        
def category_data_by_id(category_id: Union[ObjectId, str]) -> Union[dict, str]:
    obj_id = to_ObjectId(category_id)
    if obj_id is not None:
        data = db.collections["Worlds"].find_one({"_id": obj_id})
        if data is not None:
            return data
    return ""

def dump_category_data(world_name: str, category_name: str, data: dict):
    dump_json(os.path.join(world_path(world_name), category_name, data))

#endregion Category Functions

