from flask import Flask, abort, redirect, render_template, jsonify, url_for
import json
import os

app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.do')

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

@app.route('/')
def index():
    world_names = [world.replace('.json', '') for world in os.listdir(worlds_dir) if world.endswith('.json')] 
    return render_template('index.html', world_names=world_names)

@app.route("/api/world/<world_name>", methods=['GET'])
def api_world(world_name):
    world_file = f"{world_name}.json"
    world_path = os.path.join('Worlds', world_file)

    if not os.path.exists(world_path): 
        abort(404)

    with open(world_path, 'r') as f:
        world_data = json.load(f)

    
    return jsonify(world_data)

@app.route('/world/<world_name>', methods=['GET'])
def world(world_name):
    world_file = f"{world_name}.json"
    world_path = os.path.join('Worlds', world_file)

    if not os.path.exists(world_path): 
        abort(404)

    with open(world_path, 'r') as f:
        world_data = json.load(f)
    world_data = {k: world_data.get(k) for k in world_data if k != 'world_name'}
    
    return render_template('world.html', world_name=world_name, world_data=world_data)

@app.route('/world/<world_name>/<category>', methods=['GET'])
def category(world_name, category):
    world_name += ".json"
    world_data = load_json(os.path.join('Worlds', world_name))
    categories = {k: world_data.get(k) for k in world_data if k != 'world_name'}

    if categories.get(category) is None:
        redirect(url_for('world', world_name=world_name))

    category_url = f"{category}.html"

    return render_template(category_url, world_name=world_name, category=category)
    
 
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True) 
