#region Web Routes

import os
from flask import render_template, current_app


def index():
    world_names = [world.replace('.json', '') for world in os.listdir(current_app.config['WORLDS_DIR'])] 
    return render_template('index.html', world_names=world_names)


def world(world_name):
    # data = world_data(world_name)
    # data.pop("_id")
    # data["world_name"] = world_name
    # data.pop("WorldName")
    data = {}
    
    return render_template('world.html', world_name=world_name, world_data=data)

#endregion Web Routes