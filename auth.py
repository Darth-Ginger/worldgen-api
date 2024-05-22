
#region Decorators
from functools import wraps

from flask import abort, app, request


def has_Key():
    """ Decorator to enforce API Key """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # If the Auth header doesn't exist, abort
            if not request.headers.get('Authorization'):
                abort(401, description="Access Forbidden: Unauthorized")

            auth_head = request.headers['Authorization']
            # If the auth header doesn't include the secret, abort
            if auth_head != app.config['API_SECRET_KEY']:
                abort(403, description="Access Forbidden: insufficient permissions")
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def check_body(required_fields = []):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if any(field not in request.json for field in required_fields):
                abort(400, description="Bad Request: Missing required fields")
            return fn(*args, **kwargs)

        return wrapper

    return decorator
#endregion Decorators
