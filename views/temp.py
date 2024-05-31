import os

os.chdir('views')
views = [view for view in os.listdir() if view not in ['__init__.py', 'crud_view.py', 'temp.py']]

# print(views)
for view in views:
    with open(view, 'w') as f:
        view_name = view.split('.')[0]
        view_name = view_name[0].upper() + view_name[1:]
        f.write("from .crud_view import CRUDView\n\n")
        f.write(f"class {view_name}View(CRUDView):\n    collection_name = '{view_name}'")