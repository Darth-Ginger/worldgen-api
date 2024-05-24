import re
from apiflask import APIFlask, abort, HTTPTokenAuth
from flask import render_template, jsonify, request, url_for
import json
import os

from flask.views import MethodView
import custom_schemas



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
   
schema_class = {c: getattr(custom_schemas, c) for c in dir(custom_schemas) if not c.startswith('_') and not c.endswith('_')}


worlds_dir = 'Worlds'
if os.getenv('API_SECRET_KEY'):
    app.config['API_SECRET_KEY'] = os.getenv('API_SECRET_KEY')
    
    
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

def load_json(filepath: str):
    with open(filepath, 'r') as file:
        return json.load(file)

def world_exists(world_name: str) -> bool:
    return os.path.exists(os.path.join(worlds_dir, f"{world_name}"))

def category_exists(world_name: str, category_name: str) -> bool:
    if not category_name.endswith('.json'):
        category_name += '.json'
    if world_exists(world_name):
        return os.path.exists(os.path.join(worlds_dir, f"{world_name}", f"{category_name}"))
    else:
        abort(404, "World not found")
        
def get_world_path(world_name: str) -> str:
    if world_exists:
        return os.path.join(worlds_dir, f"{world_name}")
    else:
        abort(404, "World not found")

def get_world_categories(world_name: str) -> list:
    if world_exists(world_name):
        return [category for category in os.listdir(get_world_path(world_name)) if category.endswith('.json')]
    else:
        abort(404, "World not found")

def get_world_data(world_name: str) -> dict:
    if world_exists(world_name):
        world_categories = get_world_categories(world_name)
        return {
            category.replace('.json', ''): get_category_data(world_name, category) 
            for category in world_categories
        }
    else:
        abort(404, "World not found")

def get_category_data(world_name: str, category_name: str) -> dict:
    if not category_name.endswith('.json'):
        category_name += '.json'
    if world_exists(world_name) and category_exists(world_name, category_name):
        return load_json(os.path.join(worlds_dir, f"{world_name}", f"{category_name}"))
    else:
        abort(404, "World or Category not found")

def dump_json(filepath: str, data: dict):
    if not filepath.endswith('.json'):
        filepath += '.json'
    with open(filepath, 'w') as file:
        json.dump(data, file, indent=4)

def dump_world_data(world_name: str, data: dict):
    if world_exists(world_name):
        dump_json(get_world_path(world_name), data)
    else:
        abort(404, "World not found")
        
def dump_category_data(world_name: str, category_name: str, data: dict):
    if world_exists(world_name) and category_exists(world_name, category_name):
        dump_json(get_world_path(world_name), data)
    else:
        abort(404, "World or Category not found")
        
def dump_new_category_data(world_name: str, category_name: str, data: dict):
    if world_exists(world_name) and not category_exists(world_name, category_name):
        dump_json(get_world_path(world_name), data)
    else:
        abort(404, "World or Category not found")

def patch_dict(original: dict, patch: dict) -> dict:
    for key, value in patch.items():
        if isinstance(value, dict):
            original[key] = patch_dict(original.get(key, {}), value)
        else:
            original[key] = value
    return original
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
    world_data = get_world_data(world_name)
    
    world_data["kingdoms"] = {
        name: data
        for name, data in world_data["groups"].items()
        if data["type"] == "Kingdom"
    }
    world_data["factions"] = {
        name: data
        for name, data in world_data["groups"].items()
        if data["type"] != "Faction"
    }
    
    world_data.pop("groups")
    print(world_data)
    
    return render_template('world.html', world_name=world_name, world_data=world_data)

#endregion Web Routes

#region API Routes

#region API World
class API_World(MethodView):
    
    decorators = [app.auth_required, app.output(schema_class["WorldSchema"])]
    
    @app.doc(operation_id="get_api_world", responses={200: "Success", 404: "World not found"})
    def get(self,world_name):
        """
        Retrieves the JSON data of a specific world by its name.
    
        Parameters:
            world_name (str): The name of the world to retrieve the data for.
    
        Returns:
            dict: A JSON object containing the data of the specified world.
    
        Raises:
            404: If the specified world does not exist.
        """
        
        if not world_exists(world_name): 
            abort(404, "World not found")
            
        world_data = get_world_data(world_name)
    
        return jsonify(world_data)
    
    @app.input(schema_class["WorldSchema"](partial=True), location="json")
    @app.doc(operation_id="patch_api_world", responses={200: "Success", 404: "World not found"})
    def patch(world_name, patch):
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
        
        if not world_exists(world_name): 
            abort(404, "World not found")
        world_data = get_world_data(world_name)
        world_data = patch_dict(world_data, patch)
        dump_world_data(world_name, world_data)
    
        return jsonify(world_data)


#endregion API World
#region API Groups
class API_Groups(MethodView):
    
    decorators = [app.auth_required, app.output(schema_class["GroupSchema"])]
    responses  = {200: "Success", 404: "World or Category not found"}
    
    @app.doc(operation_id="get_api_groups")
    def get(self,world_name):
        """
        Retrieves the JSON data of a specific world by its name.
    
        Parameters:
            world_name (str): The name of the world to retrieve the data for.
    
        Returns:
            dict: A JSON object containing the data of the specified world.
    
        Raises:
            404: If the specified world does not exist.
        """
        
        if category_exists(world_name, "groups"):
            return get_category_data(world_name, "groups")
        else:
            abort(404, "World or Category not found")

    @app.input(schema_class["GroupSchema"](partial=True), location="json")
    @app.doc(operation_id="patch_api_groups", )
    def patch(self,world_name):
        """
        Patches the JSON data of the 'groups' category for a specific world.

        Args:
            world_name (str): The name of the world.

        Returns:
            None: If the 'groups' category exists for the world and the patch operation is successful.

        Raises:
            None: If the 'groups' category does not exist for the world.
        """
        if category_exists(world_name, "groups"):
            patched_data = patch_dict(get_category_data(world_name, "groups"), request.get_json())
            dump_category_data(world_name, "groups", patched_data)
        else:
            abort(404, "Groups not found") 

    @app.input(schema_class["GroupSchema"], location="json")
    @app.doc(operation_id="put_api_groups")
    def put(self,world_name):
        dump_new_category_data(world_name, "groups", request.get_json())
            
#endregion API Groups           
            
               
#endregion API Routes


app.add_url_rule('/api/world/<string:world_name>', view_func=API_World.as_view('api_world'))
app.add_url_rule('/api/<string:world_name>/groups', view_func=API_Groups.as_view('api_groups'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True) 
   
