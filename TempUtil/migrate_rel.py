import pymongo
import json

client = pymongo.MongoClient("mongodb://172.20.1.3:27017/")
db = client.WorldGen
collection = db.Worlds

collections = {
    "Kingdoms": db.Groups,
    "Factions": db.Groups,
    "Leaders": db.Leaders,
    "Relationships": db.Relationships,
    "MagicSystems": db.Magic,
    "Eras": db.Eras,
    "Pantheon": db.Gods
  }

Arinthia = collection.find_one({'WorldName': 'Arinthia'})

for name,data in collections.items():
    obj_data = data.find()
    if name in ["Kingdoms", "Factions"]:
        obj_data = [obj for obj in obj_data if obj['type'] == name[:-1]]
    obj_ids = [obj["_id"] for obj in obj_data]

    Arinthia[name] = obj_ids
    collection.update_one({'WorldName': 'Arinthia'}, {'$set': {name: obj_ids}})
    # print(f"{name}: {obj_ids}")


