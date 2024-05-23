from apiflask import APIFlask, abort, HTTPTokenAuth
from marshmallow.fields import Raw, String, Dict
from marshmallow.validate import OneOf
from flask import render_template, jsonify, url_for
import json
import os
import schemas


#region app setup

# app = Flask(__name__)
app = APIFlask(__name__, title='Worldgen API', version='1.0.0')
app.config['SYNC_LOCAL_SPEC'] = True
app.config['LOCAL_SPEC_PATH'] = os.path.join(app.root_path, 'openapi.json')
app.config['LOCAL_SPEC_JSON_INDENT'] = 4

app.jinja_env.add_extension('jinja2.ext.do')

auth = HTTPTokenAuth(scheme='ApiKey', header='X-API-KEY')

app.security_schemes = {
    'ApiKeyAuth': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-API-KEY'
    }
}


worlds_dir = 'Worlds'
if os.getenv('API_SECRET_KEY'):
    app.config['API_SECRET_KEY'] = os.getenv('API_SECRET_KEY')
    
schema_class = {c: getattr(schemas, c) for c in dir(schemas) if not c.startswith('_') and not c.endswith('_')}

#endregion App setup

#region Utility Functions

@app.context_processor
def inject_sidebar():
    """Injects the directory contents into the template context."""
    
    worlds = []
    
    for root, dirs, files in os.walk(worlds_dir):
        for file_name in files:
            world_data = load_json(os.path.join(root, file_name))
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

#region Security Functions

@auth.verify_token
def verify_token(token):
    return token if token == app.config['API_SECRET_KEY'] else None

#endregion Security Functions

#region Web Routes

@app.get('/')
def index():
    world_names = [world.replace('.json', '') for world in os.listdir(worlds_dir) if world.endswith('.json')] 
    return render_template('index.html', world_names=world_names)


@app.get('/world/<string:world_name>')
def world(world_name):
    world_file = f"{world_name}.json"
    world_path = os.path.join('Worlds', world_file)

    if not os.path.exists(world_path): 
        abort(404)
        

    with open(world_path, 'r') as f:
        world_data = json.load(f)
    world_data = {k: world_data.get(k) for k in world_data if k != 'world_name'}
    
    return render_template('world.html', world_name=world_name, world_data=world_data)

#endregion Web Routes

#region API Routes

@app.get("/api/world/<string:world_name>")
@app.doc(operation_id="get_api_world", responses={200: "Success", 404: "World not found"})
@app.output(schema_class["WorldSchema"])
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
    
    print(world_name)
    world_file = f"{world_name}.json"
    world_path = os.path.join('Worlds', world_file)

    if not os.path.exists(world_path): 
        abort(404, description="World not found")
        

    with open(world_path, 'r') as f:
        world_data = json.load(f)

    return jsonify(world_data)


def patch_world(world, patch):
    """
    Patches a WorldSchema with a Partial WorldSchema or a Nested Schema.

    Parameters:
        world (dict): The original WorldSchema.
        patch (dict): The patch to apply to the WorldSchema.

    Returns:
        dict: The updated WorldSchema.
    """
    if isinstance(patch, dict):
        for key, value in patch.items():
            if key in world:
                if isinstance(value, dict):
                    world[key] = patch_world(world[key], value)
                else:
                    world[key] = value
    return world


@app.patch("/api/world/<string:world_name>")
@app.doc(operation_id="patch_api_world", responses={200: "Success", 404: "World not found"})
# @app.input(schema_class["OneOfSchema"], location="json")
@app.input(Dict(keys=String(title="Schema"), values=Raw(title="Value")), location="json")
@app.output(schema_class["WorldSchema"])
def patch_api_world(world_name, patch):
    """
    Patches the JSON data of a specific world by its name.

    Parameters:
        world_name (str): The name of the world to patch the data for.
        patch (dict): The patch to apply to the world.

    Returns:
        dict: A JSON object containing the patched data of the specified world.

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

    world_data = patch_world(world_data, patch)

    with open(world_path, 'w') as f:
        json.dump(world_data, f, indent=4)

    return jsonify(world_data)


#endregion API Routes

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True) 
   
