from apiflask import Schema
from apiflask.fields import String, Integer, List, Nested
from marshmallow.validate import OneOf

Group_Types  = ["Kingdom", "Faction"]
Agenda_Types = ["Political", "Military", "Religious"]
Goal_Types   = ["Power", "Wealth", "Control"]

class KindomPropertySchema(Schema):
    race       = String(title='Race', description='Race of the property')
    capital    = String(title='Capital', description='Capital of the property')
    population = Integer(title='Population', description='Population of the property')
    
class GroupSchema(Schema):
    name               = String(title='Name', description='Name of the group'),
    short_name         = String(title='Short Name', description='Short name of the group')
    type               = String(title='Type', description='Type of the group', validate=OneOf(Group_Types))
    agenda             = String(title='Agenda', description='Agenda of the group', validate=OneOf(Agenda_Types))
    goal               = String(title='Goal', description='Goal of the group', validate=OneOf(Goal_Types))
    leadership         = String(title='Leadership', description='Leadership of the group')
    relationships      = List(String(title="Relation", description="Name of the relationship"))
    kingdom_properties = Nested('KindomPropertySchema', title='Kingdom Properties', 
                                description='Kingdom properties of the group', required=False)