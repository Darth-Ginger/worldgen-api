from apiflask import Schema
from apiflask.fields import String, List, Integer, Nested

class IntelligenceSchema(Schema):
    level         = String(title='Level', description='Level of the intelligence')
    schemes       = List(String(title='Scheme', description='Scheme of the intelligence'))
    known_schemes = List(String(title='Known Scheme', description='Known scheme of the intelligence'))
    
class RelationshipSchema(Schema):
    reputation   = Integer(title='Reputation', description='Reputation of the relationship')
    intelligence = Nested('IntelligenceSchema', title='Intelligence', description='Intelligence of the relationship')    