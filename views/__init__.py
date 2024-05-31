import os
import importlib
from flask import Flask

def register_views(app: Flask):
    # Get all .py files in the views directory except __init__.py and crud_view.py
    views_dir = os.path.dirname(__file__)
    view_files = [f[:-3] for f in os.listdir(views_dir) if f.endswith('.py') and f not in ('__init__.py', 'crud_view.py')]

    for view_file in view_files:
        try:
            # Dynamically import the module
            module = importlib.import_module(f'.{view_file}', package='views')
            # Retrieve the view class
            view_class = getattr(module, 'view_class', None)
            if view_class:
                # Create the URL rules based on the view class name
                view_name = view_class.__name__.lower()
                app.add_url_rule(f'/{view_name}/', view_func=view_class.as_view(view_name), methods=['GET', 'POST'])
                app.add_url_rule(f'/{view_name}/<string:object_id>/', view_func=view_class.as_view(f'{view_name}_with_id'), methods=['GET', 'PUT', 'PATCH', 'DELETE'])
        except ImportError as e:
            app.logger.error(f"Error importing {view_file}: {e}")
        except AttributeError as e:
            app.logger.error(f"Error setting up {view_file}: {e}")