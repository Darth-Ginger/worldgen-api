#region World Class
from typing import Optional
from pydantic import BaseModel


class Geography(BaseModel):
    size: str
    balance: str
    landmarks: list
    description: str

class God(BaseModel):
    name: str
    domain: str
    
class Pantheon(BaseModel):
    gods: list[God]

class Magic_Source(BaseModel):
    type: str
    description: str
    users: list[str]
    rules: list[str]
    notes: str
    examples: dict

class Magic(BaseModel):
    uses: list[str]
    sources: dict[str, Magic_Source]

class Intel(BaseModel):
    level: str
    schemes: list[str]
    known_schemes: list[str]
    
class Relationship(BaseModel):
    reputation: int
    intelligence: Intel

class Kingdom(BaseModel):
    name: str
    race: str
    capital: str
    population: int
    leadership: str
    relationships: dict[str, Relationship]
    
class Faction(BaseModel):
    type: str
    goal: str
    leadership: str
    relationships: dict[str, Relationship]

class Leader(BaseModel):
    kingdom: Optional[str]
    faction: Optional[str]
    traits: list[str]
    goals: list[str]
    relationships: dict[str, Relationship]

class Period(BaseModel):
    period: str
    major_events: list[str]
    minor_events: list[str]
    perspective: dict[str, str]

class Era(BaseModel):
    dict[str, Period]

class World(BaseModel):
    world_name: str
    geography: Geography
    pantheon: Pantheon
    magic: Magic
    kingdoms: dict[str, Kingdom]
    factions: dict[str, Faction]
    leaders: dict[str, Leader]
    history: dict[str, Era]
    
class Category(BaseModel):
    name: str

#endregion World Class