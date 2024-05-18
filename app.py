import os
import json
from flask import Flask, jsonify, render_template

app = Flask(__name__)
data_dir = "./Worlds"  # Replace with the path to your data directory

@app.context_processor
def inject_sidebar():
    """Injects the directory contents into the template context."""
    sidebar_items = os.listdir(data_dir)
    return {"sidebar_items": sidebar_items}

@app.route('/')
def index():
    worlds = os.listdir(data_dir)
    
    return render_template('worlds_page.html', worlds=worlds) 

@app.route('/<world>')
def get_world(world):
    world_dir = os.path.join(data_dir, world)
    world_data = os.listdir(world_dir)
    if os.path.isdir(world_dir):
        return render_template('world_page.html', world=world, world_data=world_data)
    return 

@app.route('/<world>/<filename>')
def get_data(world, filename):
    if ".json" not in filename:
        filename = f"{filename}.json"
    file_path = os.path.join(data_dir, world, f"{filename}")
    if os.path.exists(file_path):
        with open(file_path) as f:
            data = json.load(f)
        return jsonify(data)
    else:
        return "File not found", 404

if __name__ == '__main__':
    app.run(debug=True)
