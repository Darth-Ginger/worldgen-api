from apiflask import Blueprint, jsonify, request
from utils import load_json, dump_json, check_existence, abort_if_not_found
import os

world_bp = Blueprint('world', __name__, url_prefix='/api/world')

@world_bp.route('/')
def index():
    world_names = [world.replace('.json', '') for world in os.listdir('Worlds')]
    return jsonify(world_names)

@world_bp.route('/<string:world_name>')
def get_world(world_name):
    world_path = f'Worlds/{world_name}.json'
    abort_if_not_found(check_existence(world_path), f'World {world_name} not found')
    world_data = load_json(world_path)
    return jsonify(world_data)

# Additional routes can be added here similarly
