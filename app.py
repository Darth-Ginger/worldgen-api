from apiflask import APIFlask
from config import Config
from endpoints.web_endpoints import index, world
from views import register_views
from db import DB_Connection

#region app setup

app = APIFlask(__name__, title='Worldgen API', version='1.0.0')
app.config.from_object(Config)
db = DB_Connection()

@app.context_processor
def inject_sidebar():
    """Injects the directory contents into the template context."""
    sidebar_items = db.all_collection_documents('Worlds')
    sidebar_items = [world["WorldName"] for world in sidebar_items]
    print(sidebar_items)
    return {"sidebar_items": sidebar_items}

app.jinja_env.add_extension('jinja2.ext.do')
    
#@TODO: Register Blueprints and URL Rules   
## Web Views
app.add_url_rule('/', view_func=index, methods=['GET'])
app.add_url_rule('/world/<string:world_name>', view_func=world, methods=['GET'])  

## API Views
register_views(app)
  
#endregion App setup

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True) 
   
