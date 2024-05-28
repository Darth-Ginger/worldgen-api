#region Web Routes

import os
from flask import app, render_template

from utils import world_data


@app.get('/')
def index():
    world_names = [world.replace('.json', '') for world in os.listdir(app.config['WORLDS_DIR'])] 
    return render_template('index.html', world_names=world_names)


@app.get('/world/<string:world_name>')
def world(world_name):
    data = world_data(world_name)
    
    data["kingdoms"] = {
        name: data
        for name, data in data["groups"].items()
        if data["type"] == "Kingdom"
    }
    data["factions"] = {
        name: data
        for name, data in world_data["groups"].items()
        if data["type"] != "Faction"
    }
    
    data.pop("groups")
    # print(world_data)
    
    return render_template('world.html', world_name=world_name, world_data=data)

#endregion Web Routes