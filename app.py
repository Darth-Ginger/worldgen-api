from typing import Dict
from flask import Flask, abort, render_template, jsonify, url_for
import json
import os

app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.do')


#endregion App setup

worlds_dir = 'Worlds'

#region Utility Functions

@app.context_processor
def inject_sidebar():
    """Injects the directory contents into the template context."""
    
    worlds = []
    
    for root, dirs, files in os.walk(worlds_dir):
        for dir_name in dirs:
            world = {
                'name': dir_name,
                'url': url_for('world', world_name=dir_name)
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

@app.get('/')
def index():
    return render_template('index.html')

@app.route('/world/<world_name>')
def world(world_name):
    base_dir = os.path.join(worlds_dir, world_name)
    
    if not os.path.exists(base_dir):
        abort(404)

    def load_json(file_name):
        file_path = os.path.join(base_dir, file_name)
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return None


    world_description = load_json('01_world_description.json')
    pantheon = load_json('02_pantheon.json')
    magic_system = load_json('03_magic_system.json')
    factions = load_json('04_factions.json')
    kingdoms = load_json('05_kingdoms.json')
    leaders = load_json('06_key_leaders.json')
    history_chunks = load_json('07_history_chunks.json')

    return render_template(
        'world.html', 
        world_name=world_name, 
        world_description=world_description,
        kingdoms=kingdoms,
        factions=factions,
        pantheon=pantheon,
        magic_system=magic_system,
        history_chunks=history_chunks,
        leaders=leaders
    )

@app.route('/world/<world_name>/kingdoms')
def kingdoms(world_name):
    filepath = os.path.join('Worlds', world_name, 'kingdoms.json')
    data = load_json(filepath)
    return render_template('kingdoms.html', kingdoms=data['kingdoms'], world_name=world_name)

@app.route('/world/<world_name>/factions')
def factions(world_name):
    filepath = os.path.join('Worlds', world_name, 'factions.json')
    data = load_json(filepath)
    return render_template('factions.html', factions=data['factions'], world_name=world_name)

@app.route('/world/<world_name>/leaders')
def leaders(world_name):
    filepath = os.path.join('Worlds', world_name, 'leaders.json')
    data = load_json(filepath)
    return render_template('leaders.html', leaders=data['leaders'], world_name=world_name)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True) 
   
