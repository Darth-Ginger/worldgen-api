# # type: ignore

from .geography_schema import GeographySchema
from .group_schema     import GroupSchema,    KindomPropertySchema
from .leader_schema    import LeaderSchema
from .magic_schema     import MagicSchema,    MagicSourceSchema
from .pantheon_schema  import PantheonSchema, GodSchema
from .world_schema     import WorldSchema

#region Basic Schemas

Group_Types  = ["Kingdom", "Faction"]
Agenda_Types = ["Political", "Military", "Religious"]
Goal_Types   = ["Power", "Wealth", "Control"]