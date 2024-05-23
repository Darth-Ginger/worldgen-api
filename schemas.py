# # type: ignore


from apiflask import Schema
from apiflask.fields import String, Integer, List, Nested, Dict


class GeographySchema(Schema):
    size = String(title='Size', description='Size of the world')
    balance = String(title='Balance', description='Balance of the world')
    landmarks = Dict(keys=String(title="Name", description="Name of the landmark"), 
                     values=String(title='Landmark', description='Landmark of the world'))
    description = String(title='Description', description='Description of the world')

class GodSchema(Schema):
    name = String(title='Name', description='Name of the god')
    domain = String(title='Domain', description='Comma separated list of domains of the god')

class PantheonSchema(Schema):
    gods = Dict(keys=String(title="Name", description="Name of the god"), 
                values=Nested('GodSchema', title='God', description='Information about a god in the pantheon'))

class MagicSchema(Schema):
    uses = String(title='Uses', description='Comma separated list of magic uses')
    sources = Dict(keys=String(title="Name", description="Name of the source"), 
                   values=Nested('Magic_SourceSchema', title='Source', description='Information about a source in the magic system'))

class Magic_SourceSchema(Schema):
    type = String(title='Type', description='Type of the source')
    description = String(title='Description', description='Description of the source')
    users = List(String(title='Users', description='List of users for the magic source'))
    rules = List(String(title='Rules', description='List of rules for the magic source'))
    notes = String(title='Notes', description='Notes on the source')
    examples = Dict(keys=String(title="Name", description="Name of the example spell"),
                    values=String(title='Spell', description='Description of the spell'))

class IntelligenceSchema(Schema):
    level = String(title='Level', description='Level of the intelligence')
    schemes = List(String(title='Scheme', description='Scheme of the intelligence'))
    known_schemes = List(String(title='Known Scheme', description='Known scheme of the intelligence'))

class RelationshipSchema(Schema):
    reputation = Integer(title='Reputation', description='Reputation of the relationship')
    intelligence = Nested('IntelligenceSchema', title='Intelligence', description='Intelligence of the relationship')
   
class KingdomSchema(Schema):
    name = String(title='Name', description='Name of the kingdom')
    race = String(title='Race', description='Race of the kingdom')
    capital = String(title='Capital', description='Capital of the kingdom')
    population = Integer(title='Population', description='Population of the kingdom')
    leadership = String(title='Leadership', description='Leadership of the kingdom')
    relationships = Dict(keys=String(title="Name", description="Name of the relationship"), 
                         values=Nested('RelationshipSchema', title='Relationship', description='Information about a relationship in the kingdom'))

class FactionSchema(Schema):
    type = String(title='Type', description='Type of the faction')
    goal = String(title='Goal', description='Goal of the faction')
    leadership = String(title='Leadership', description='Leadership of the faction')
    relationships = Dict(keys=String(title="Name", description="Name of the relationship"),
                         values=Nested('RelationshipSchema', title='Relationship', description='Information about a relationship in the faction'))
    
class LeaderSchema(Schema):
    kingdom = String(title='Kingdom', description='Kingdom of the leader', required=False)
    faction = String(title='Faction', description='Faction of the leader', required=False)
    traits = List(String(title='Trait', description='Trait of the leader'))
    goals = List(String(title='Goal', description='Goal of the leader'))
    relationships = Dict(keys=String(title="Name", description="Name of the relationship"),
                         values=Nested('RelationshipSchema', title='Relationship', description='Information about a relationship in the leader'))
                       
class PeriodSchema(Schema):
    period = String(title='Period', description='Period of the era')
    major_events = List(String(title='Major Event', description='Major event of the era'))
    minor_events = List(String(title='Minor Event', description='Minor event of the era'))
    perspective = Dict(keys=String(title="Name", description="Name of the perspective"),
                        values=String(title='Perspective', description='Perspective of the era'))
    
class EraSchema(Schema):
    periods = Dict(keys=String(title="Name", description="Name of the period"),
                   values=Nested('PeriodSchema', title='Period', description='Information about a period in the era'))
    
    

                        
class WorldSchema(Schema):
    world_name = String(title='World Name', description='Name of the world')
    geography = Nested('GeographySchema', title='Geography', description='Information about the geography of the world')
    pantheon = Nested('PantheonSchema', title='Pantheon', description='Information about the pantheon of the world')
    magic = Nested('MagicSchema', title='Magic', description='Information about the magic system of the world')
    kingdoms = Dict(keys=String(), values=Nested('KingdomSchema', title='Kingdom', description='Information about a kingdom in the world'))
    factions = Dict(keys=String(), values=Nested('FactionSchema', title='Faction', description='Information about a faction in the world'))
    leaders = Dict(keys=String(), values=Nested('LeaderSchema', title='Leader', description='Information about a leader in the world'))
    history = Dict(keys=String(), values=Nested('EraSchema', title='Era', description='Information about an era in the world'))

