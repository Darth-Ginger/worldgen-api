import inspect
from flask import Blueprint, app, jsonify, request, current_app
from apiflask import Schema, input, output, abort
from marshmallow import ValidationError
from utils import load_json, dump_json, check_existence, abort_if_not_found


entity_bp = Blueprint('entity', __name__)

SCHEMA_CLASSES = app.config['SCHEMA_CLASSES']


def get_schema(entity_type):
    schema_class = SCHEMA_CLASSES.get(entity_type)
    if not schema_class:
        abort(400, message=f"No schema defined for entity type: {entity_type}")
    return schema_class()

@entity_bp.route('/<entity_type>', methods=['GET'])
@output(Schema(many=True))  # Replace Schema with a more generic response schema if needed
def get_entities(entity_type):
    schema = get_schema(entity_type)
    # Load entities from database or file (this is a placeholder)
    entities = []
    return entities

@entity_bp.route('/<entity_type>', methods=['POST'])
@input(Schema)  # Replace Schema with a more generic input schema if needed
@output(Schema)  # Replace Schema with a more generic response schema if needed
def create_entity(entity_type):
    schema = get_schema(entity_type)
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        abort(400, message=err.messages)
    
    # Save the new entity (this is a placeholder)
    return data, 201
