from flask import Flask, render_template, jsonify, url_for
import json
import os


app = Flask(__name__)

worlds_dir = 'Worlds'


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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/world/<world_name>')
def world(world_name):
    world_dir = os.path.join('Worlds', world_name)
    if not os.path.exists(world_dir):
        return "World not found", 404
    description = load_json(os.path.join(world_dir, '01_world_description.json'))
    return render_template('world.html', world_name=world_name, description=description)

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
