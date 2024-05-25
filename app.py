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
    
    for world in os.listdir(worlds_dir):
        
        world = {
            'name': world,
            'url': url_for('world', world_name=world)
        }
        worlds.append(world)
        
    
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
    world_names = [world.replace('.json', '') for world in os.listdir(worlds_dir)] 
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
    # print(world_data)
    
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
            path = request.path
            if path.endswith('/kingdoms'):
                return get_category_data(world_name, "kingdoms")
            elif path.endswith('/factions'):
                return get_category_data(world_name, "factions")
            else:
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

#region API magic

class API_Magic(MethodView):
    
    decorators = [app.auth_required, app.output(schema_class["MagicSchema"])]
    
    @app.doc(operation_id="get_api_magic")
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
        if category_exists(world_name, "magic"):
            return get_category_data(world_name, "magic")
        else:
            abort(404, "World or Category not found")

    @app.input(schema_class["MagicSchema"](partial=True), location="json")
    @app.doc(operation_id="patch_api_magic")
    def patch(self,world_name):
        """
        Patches the JSON data of the 'magic' category for a specific world.

        Args:
            world_name (str): The name of the world.

        Returns:
            None: If the 'magic' category exists for the world and the patch operation is successful.

        Raises:
            None: If the 'magic' category does not exist for the world.
        """
        if category_exists(world_name, "magic"):
            patched_data = patch_dict(get_category_data(world_name, "magic"), request.get_json())
            dump_category_data(world_name, "magic", patched_data)
        else:
            abort(404, "magic not found")
            
    @app.input(schema_class["MagicSchema"], location="json")
    @app.doc(operation_id="put_api_magic")
    def put(self,world_name):
        dump_new_category_data(world_name, "magic", request.get_json())

#endregion API magic

#region API leaders

class API_Leaders(MethodView):
    
    decorators = [app.auth_required, app.output(schema_class["LeaderSchema"])]
    
    @app.doc(operation_id="get_api_leaders")
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
        if category_exists(world_name, "leaders"):
            return get_category_data(world_name, "leaders")
        else:
            abort(404, "World or Category not found")

    @app.input(schema_class["LeaderSchema"](partial=True), location="json")
    @app.doc(operation_id="patch_api_leaders")
    def patch(self,world_name):
        """
        Patches the JSON data of the 'leaders' category for a specific world.

        Args:
            world_name (str): The name of the world.

        Returns:
            None: If the 'leaders' category exists for the world and the patch operation is successful.

        Raises:
            None: If the 'leaders' category does not exist for the world.
        """
        if category_exists(world_name, "leaders"):
            patched_data = patch_dict(get_category_data(world_name, "leaders"), request.get_json())
            dump_category_data(world_name, "leaders", patched_data)
        else:
            abort(404, "leaders not found")
            
    @app.input(schema_class["LeaderSchema"], location="json")
    @app.doc(operation_id="put_api_leaders")
    def put(self,world_name):
        dump_new_category_data(world_name, "leaders", request.get_json())

#endregion API leaders

#region API Geo

class API_Geography(MethodView):
    
    decorators = [app.auth_required, app.output(schema_class["GeographySchema"])]
    
    @app.doc(operation_id="get_api_geography")
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
        if category_exists(world_name, "geography"):
            return get_category_data(world_name, "geography")
        else:
            abort(404, "World or Category not found")

    @app.input(schema_class["GeographySchema"](partial=True), location="json")
    @app.doc(operation_id="patch_api_geography")
    def patch(self,world_name):
        """
        Patches the JSON data of the 'leaders' category for a specific world.

        Args:
            world_name (str): The name of the world.

        Returns:
            None: If the 'geography' category exists for the world and the patch operation is successful.

        Raises:
            None: If the 'geography' category does not exist for the world.
        """
        if category_exists(world_name, "geography"):
            patched_data = patch_dict(get_category_data(world_name, "geography"), request.get_json())
            dump_category_data(world_name, "geography", patched_data)
        else:
            abort(404, "geography not found")
            
    @app.input(schema_class["GeographySchema"], location="json")
    @app.doc(operation_id="put_api_geography")
    def put(self,world_name):
        dump_new_category_data(world_name, "geography", request.get_json())

#endregion API Geo       
 
#region API Relationships

class API_Relationships(MethodView):
    
    decorators = [app.auth_required, app.output(schema_class["RelationshipSchema"])]
    
    @app.doc(operation_id="get_api_relationships")
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
        if category_exists(world_name, "relationships"):
            return get_category_data(world_name, "relationships")
        else:
            abort(404, "World or Category not found")

    @app.input(schema_class["RelationshipSchema"](partial=True), location="json")
    @app.doc(operation_id="patch_api_relationships")
    def patch(self,world_name):
        """
        Patches the JSON data of the 'leaders' category for a specific world.

        Args:
            world_name (str): The name of the world.

        Returns:
            None: If the 'relationships' category exists for the world and the patch operation is successful.

        Raises:
            None: If the 'relationships' category does not exist for the world.
        """
        if category_exists(world_name, "relationships"):
            patched_data = patch_dict(get_category_data(world_name, "relationships"), request.get_json())
            dump_category_data(world_name, "relationships", patched_data)
        else:
            abort(404, "relationships not found")
            
    @app.input(schema_class["RelationshipSchema"], location="json")
    @app.doc(operation_id="put_api_relationships")
    def put(self,world_name):
        dump_new_category_data(world_name, "relationships", request.get_json())

#endregion API Relationships            
      
#region API Pantheon

class API_Pantheon(MethodView):
    
    decorators = [app.auth_required, app.output(schema_class["PantheonSchema"])]
    
    @app.doc(operation_id="get_api_pantheon")
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
        if category_exists(world_name, "pantheon"):
            return get_category_data(world_name, "pantheon")
        else:
            abort(404, "World or Category not found")

    @app.input(schema_class["PantheonSchema"](partial=True), location="json")
    @app.doc(operation_id="patch_api_pantheon")
    def patch(self,world_name):
        """
        Patches the JSON data of the 'leaders' category for a specific world.

        Args:
            world_name (str): The name of the world.

        Returns:
            None: If the 'pantheon' category exists for the world and the patch operation is successful.

        Raises:
            None: If the 'pantheon' category does not exist for the world.
        """
        if category_exists(world_name, "pantheon"):
            patched_data = patch_dict(get_category_data(world_name, "pantheon"), request.get_json())
            dump_category_data(world_name, "pantheon", patched_data)
        else:
            abort(404, "pantheon not found")
            
    @app.input(schema_class["PantheonSchema"], location="json")
    @app.doc(operation_id="put_api_pantheon")
    def put(self,world_name):
        dump_new_category_data(world_name, "pantheon", request.get_json())

#endregion API Pantheon  

#region API History

class API_History(MethodView):
    
    decorators = [app.auth_required, app.output(schema_class["EraSchema"])]
    
    @app.doc(operation_id="get_api_history")
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
        if category_exists(world_name, "history"):
            return get_category_data(world_name, "history")
        else:
            abort(404, "World or Category not found")

    @app.input(schema_class["EraSchema"](partial=True), location="json")
    @app.doc(operation_id="patch_api_history")
    def patch(self,world_name):
        """
        Patches the JSON data of the 'leaders' category for a specific world.

        Args:
            world_name (str): The name of the world.

        Returns:
            None: If the 'history' category exists for the world and the patch operation is successful.

        Raises:
            None: If the 'history' category does not exist for the world.
        """
        if category_exists(world_name, "history"):
            patched_data = patch_dict(get_category_data(world_name, "history"), request.get_json())
            dump_category_data(world_name, "history", patched_data)
        else:
            abort(404, "history not found")
            
    @app.input(schema_class["EraSchema"], location="json")
    @app.doc(operation_id="put_api_history")
    def put(self,world_name):
        dump_new_category_data(world_name, "history", request.get_json())

#endregion API History 

#endregion API Routes


app.add_url_rule('/api/world/<string:world_name>', view_func=API_World.as_view('api_world'))
app.add_url_rule('/api/world/<string:world_name>/groups', view_func=API_Groups.as_view('api_groups'))
app.add_url_rule('/api/world/<string:world_name>/kingdoms', view_func=API_Groups.as_view('api_kingdoms'))
app.add_url_rule('/api/world/<string:world_name>/factions', view_func=API_Groups.as_view('api_factions'))
app.add_url_rule('/api/world/<string:world_name>/magic', view_func=API_Magic.as_view('api_magic'))
app.add_url_rule('/api/world/<string:world_name>/leaders', view_func=API_Leaders.as_view('api_leaders'))
app.add_url_rule('/api/world/<string:world_name>/geography', view_func=API_Geography.as_view('api_geography'))
app.add_url_rule('/api/world/<string:world_name>/pantheon', view_func=API_Pantheon.as_view('api_pantheon'))
app.add_url_rule('/api/world/<string:world_name>/history', view_func=API_History.as_view('api_history'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True) 
   
