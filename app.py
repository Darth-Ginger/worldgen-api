from apiflask import APIFlask
from config import Config
from endpoints import index, world
from utils import worlds
import db
#@TODO: include Blueprints


#region app setup

# app = Flask(__name__)
app = APIFlask(__name__, title='Worldgen API', version='1.0.0')
app.config.from_object(Config)

@app.context_processor
def inject_sidebar():
    """Injects the directory contents into the template context."""
    sidebar_items = worlds()
    return {"sidebar_items": sidebar_items}

app.jinja_env.add_extension('jinja2.ext.do')
    
#@TODO: Register Blueprints and URL Rules   
app.add_url_rule('/', view_func=index, methods=['GET'])
app.add_url_rule('/world/<string:world_name>', view_func=world, methods=['GET'])  
  
#endregion App setup

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True) 
   
