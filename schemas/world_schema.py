from apiflask import Schema
from apiflask.fields import String, Nested, Dict

class WorldSchema(Schema):
    world_name = String(title='World Name', description='Name of the world')
    geography  = Nested('GeographySchema', title='Geography', description='Information about the geography of the world')
    pantheon   = Nested('PantheonSchema', title='Pantheon', description='Information about the pantheon of the world')
    magic      = Nested('MagicSchema', title='Magic', description='Information about the magic system of the world')
    groups     = Dict(keys=String(title="Name", description="Name of the group"), 
                       values=Nested('GroupSchema', title='Group', description='Information about a kingdom in the world'))
    leaders    = Dict(keys=String(title="Name", description="Name of the leader"), 
                      values=Nested('LeaderSchema', title='Leader', description='Information about a leader in the world'))
    history    = Dict(keys=String(title="Era Name", description="Name of an era"), 
                   values=Nested('EraSchema', title='Era', description='Information about an era in the world'))