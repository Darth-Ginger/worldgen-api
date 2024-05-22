from typing import Dict
from flask import Flask, abort, redirect, render_template, jsonify, url_for
import json
import os
from auth import check_body, has_Key
from flask_openapi3 import OpenAPI, Info, Tag, OAuthConfig
from pydantic import BaseModel
import objects

#region App setup

api_secret = os.getenv('API_SECRET')
if not api_secret:
    raise ValueError("API_SECRET is not set in the environment variables")

api_key = {
    "type": "apiKey",
    "in": "header",
    "name": "Authorization"
}

security_schemes = {"api_key": api_key}
info = Info(title="WorldGen-API", version="1.0.0")

app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.do')
api_app = OpenAPI(app.name, info=info, security_schemes=security_schemes)

#endregion App setup

worlds_dir = 'Worlds'

#region Utility Functions

@app.context_processor
def inject_sidebar():
    """Injects the directory contents into the template context."""
    
    worlds = []
    
    for root, dirs, files in os.walk(worlds_dir):
        for file_name in files:
            world_data = load_json(os.path.join(root, file_name))
            world = {
                'name': world_data.get('world_name'),
                'url': url_for('world', world_name=world_data.get('world_name')),
                "categories": [category for category in world_data.keys() if category != 'world_name']
            }
            worlds.append(world)
        break
    
    return dict(worlds=worlds)

def load_json(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)
def world_exists(world_name) -> bool:
    return os.path.exists(os.path.join(worlds_dir, f"{world_name}.json"))

#endregion Utility Functions

#region Web Routes

@api_app.get('/')
def index():
    world_names = [world.replace('.json', '') for world in os.listdir(worlds_dir) if world.endswith('.json')] 
    return render_template('index.html', world_names=world_names)

@api_app.get('/world/<string:world_name>')
def world(world_name: str):
    world_file = f"{world_name}.json"
    world_path = os.path.join('Worlds', world_file)

    try:
        with open(world_path, 'r') as f:
            world_data = json.load(f)
    except FileNotFoundError:
        abort(404)
    except (json.JSONDecodeError, TypeError):
        abort(500, "Invalid or missing JSON file")
    
    if world_data is None:
        abort(500, "Invalid or missing world data")
    
    world_data = {k: world_data.get(k) for k in world_data if k != 'world_name'}
    
    if world_data is None:
        abort(500, "Invalid or missing world data")
    
    return render_template('world.html', world_name=world_name, world_data=world_data)

#endregion Web Routes
#region API Endpoints

@api_app.get("/api/world/<string:world_name>", responses={"200": objects.World}, operation_id="get_api_world")
def api_world(world_name: str):
    """
    Retrieves the JSON data of a specific world by its name.

    Parameters:
        world_name (str): The name of the world to retrieve the data for.

    Returns:
        dict: A JSON object containing the data of the specified world.

    Raises:
        404: If the specified world does not exist.
    """
    
    print(world_name)
    world_file = f"{world_name}.json"
    world_path = os.path.join('Worlds', world_file)

    if not os.path.exists(world_path): 
        abort(404, description="World not found")

    with open(world_path, 'r') as f:
        world_data = json.load(f)

    return jsonify(world_data)
    
#endregion API Endpoints



if __name__ == '__main__':
    # app.run(host='0.0.0.0', debug=True) 
    api_app.run(host='0.0.0.0', debug=True)
