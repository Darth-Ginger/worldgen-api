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

#region MongoDB Functions

def serialize_doc(doc: dict) -> dict:
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            doc[key] = str(value)
    return doc



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

#endregion MongoDB Functions

