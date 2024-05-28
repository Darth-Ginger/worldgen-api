from apiflask import Schema
from apiflask.fields import String, Dict

class GeographySchema(Schema):
    size        = String(title='Size', description='Size of the world')
    balance     = String(title='Balance', description='Balance of the world')
    landmarks   = Dict(keys=String(title="Name", description="Name of the landmark"), 
                     values=String(title='Landmark', description='Landmark of the world'))
    description = String(title='Description', description='Description of the world')