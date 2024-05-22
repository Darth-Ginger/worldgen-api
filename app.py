from flask import Flask, abort, redirect, render_template, jsonify, url_for
import json
import os
from auth import check_body, has_Key
from flask_openapi3 import OpenAPI, Info, Tag, OAuthConfig
from pydantic import BaseModel

#region App setup

api_secret = os.getenv('API_SECRET')
if not api_secret:
    raise ValueError("API_SECRET is not set in the environment variables")

api_key = {
    "type": "apiKey",
    "in": "header",
    "name": "Authorization"
}

info = Info(title="WorldGen-API", version="1.0.0")

app = OpenAPI(__name__, info=info)
app.jinja_env.add_extension('jinja2.ext.do')
app.config['API_SECRET_KEY'] = f"Bearer {api_secret}"

#endregion App setup

worlds_dir = 'Worlds'

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



#region Web Routes


@app.get('/', operation_id="get_index")
def index():
    world_names = [world.replace('.json', '') for world in os.listdir(worlds_dir) if world.endswith('.json')] 
    return render_template('index.html', world_names=world_names)

@app.get('/world/<world_name>', operation_id="get_world")
def world(world_name):
    world_file = f"{world_name}.json"
    world_path = os.path.join('Worlds', world_file)

    if not os.path.exists(world_path): 
        abort(404)

    with open(world_path, 'r') as f:
        world_data = json.load(f)
    world_data = {k: world_data.get(k) for k in world_data if k != 'world_name'}
    
    return render_template('world.html', world_name=world_name, world_data=world_data)

@app.get('/world/<world_name>/<category>', operation_id="get_category")
def category(world_name, category):
    world_name += ".json"
    world_data = load_json(os.path.join('Worlds', world_name))
    categories = {k: world_data.get(k) for k in world_data if k != 'world_name'}

    if categories.get(category) is None:
        redirect(url_for('world', world_name=world_name))

    category_url = f"{category}.html"

    return render_template(category_url, world_name=world_name, category=category)
    
#endregion Web Routes
#region API Endpoints


@app.get("/api/world/<world_name>", operation_id="get_api_world")
def api_world(world_name):
    """
    Retrieves the JSON data of a specific world by its name.

    Parameters:
        world_name (str): The name of the world to retrieve the data for.

    Returns:
        dict: A JSON object containing the data of the specified world.

    Raises:
        404: If the specified world does not exist.
    """
    world_file = f"{world_name}.json"
    world_path = os.path.join('Worlds', world_file)

    if not os.path.exists(world_path): 
        abort(404, description="World not found")

    with open(world_path, 'r') as f:
        world_data = json.load(f)

    return jsonify(world_data)
 
@app.get("/api/world/<world_name>/<category>", operation_id="get_api_category")
def api_category(world_name, category):
    if not world_exists(world_name):
        abort(404, description="World not found")
    world = load_json(os.path.join('Worlds', f"{world_name}.json"))
    if category not in world:
        abort(404, description="Category not found")
    return jsonify(world[category])
    
#endregion API Endpoints

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True) 
