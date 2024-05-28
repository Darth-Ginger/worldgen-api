from apiflask import Schema
from apiflask.fields import String, List, Dict, Nested

class LeaderSchema(Schema):
    kingdom = String(title='Kingdom', description='Kingdom of the leader', required=False)
    faction = String(title='Faction', description='Faction of the leader', required=False)
    traits  = List(String(title='Trait', description='Trait of the leader'))
    goals   = List(String(title='Goal', description='Goal of the leader'))
    relationships = Dict(keys=String(title="Name", description="Name of the relationship"),
                         values=Nested('RelationshipSchema', title='Relationship', description='Information about a relationship in the leader'))