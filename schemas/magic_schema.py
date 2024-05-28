from apiflask import Schema
from apiflask.fields import String, List, Dict, Nested

class MagicSchema(Schema):
    uses    = String(title='Uses', description='Comma separated list of magic uses')
    sources = Dict(keys=String(title="Name", description="Name of the source"), 
                   values=Nested('Magic_SourceSchema', title='Source', description='Information about a source in the magic system'))

class MagicSourceSchema(Schema):
    type        = String(title='Type', description='Type of the source')
    description = String(title='Description', description='Description of the source')
    users       = List(String(title='Users', description='List of users for the magic source'))
    rules       = List(String(title='Rules', description='List of rules for the magic source'))
    notes       = String(title='Notes', description='Notes on the source')
    examples    = Dict(keys=String(title="Name", description="Name of the example spell"),
                    values=String(title='Spell', description='Description of the spell'))