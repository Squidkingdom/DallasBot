import discord
from siegeapi import Auth as APIAuth

class DBPlayer():
    def __init__(self, id, bounds = 7, discordID = None, name = None):
        self.id = id
        self.rollingBounds: int = bounds
        self.discordID:int = discordID
        self.name = name
    
    def setBounds(self, bounds: int):
        self.rollingBounds = bounds
    
    def __hash__(self) -> int:
        return hash(self.id)
    
    def __reduce__(self):
        return (DBPlayer, (self.id, self.rollingBounds, self.discordID, self.name))
    
    def __eq__(self, o: object) -> bool:
        if not isinstance(o, type(self)): return NotImplemented
        if o.__hash__() == self.__hash__():
            return True