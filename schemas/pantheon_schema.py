from apiflask import Schema
from apiflask.fields import String, Nested, Dict

class GodSchema(Schema):
    name    = String(title='Name', description='Name of the god')
    domain  = String(title='Domain', description='Comma separated list of domains of the god')
    
class PantheonSchema(Schema):
    gods = Dict(keys=String(title="Name", description="Name of the god"), 
                values=Nested('GodSchema', title='God', description='Information about a god in the pantheon'))