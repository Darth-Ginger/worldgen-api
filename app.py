from apiflask import APIFlask
from config import Config
#@TODO: include Blueprints


#region app setup

# app = Flask(__name__)
app = APIFlask(__name__, title='Worldgen API', version='1.0.0')
app.config.from_object(Config)

app.jinja_env.add_extension('jinja2.ext.do')
    
#@TODO: Register Blueprints    
    
#endregion App setup

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True) 
   
