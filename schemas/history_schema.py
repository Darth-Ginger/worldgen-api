from apiflask import Schema
from apiflask.fields import String, List, Nested, Dict

class PeriodSchema(Schema):
    period       = String(title='Period', description='Period of the era')
    major_events = List(String(title='Major Event', description='Major event of the era'))
    minor_events = List(String(title='Minor Event', description='Minor event of the era'))
    perspective  = Dict(keys=String(title="Name", description="Name of the perspective"),
                        values=String(title='Perspective', description='Perspective of the era'))
    
class EraSchema(Schema):
    periods = Dict(keys=String(title="Name", description="Name of the period"),
                   values=Nested('PeriodSchema', title='Period', description='Information about a period in the era'))