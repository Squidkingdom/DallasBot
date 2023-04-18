
import sys
sys.path.append('.')

from objects.player import DBPlayer
from siegeapi import Auth as APIAuth
from siegeapi.exceptions import InvalidRequest
import re
async def convertNameToId(name):
        auth = APIAuth(token='U3F1aWRkeXR3ZWFrc0BnbWFpbC5jb206SmF5aGF3ayoy')
        try:
            player = await auth.get_player(name=name)
            await auth.close()
        except InvalidRequest:
            await auth.close()
            return -1
        return player.id

class DBRoster:
    def __init__(self, players = []):
        self.players = players
    
    def getPlayerByDiscord(self, id):
        for i, x in enumerate(self.players):
            if x.discordID == int(id):
                return i, x
        return None, None
    
    def getPlayerByID(self,id):
        for i, x in enumerate(self.players):
            if x.id == id:
                return i, x
        return None, None

    async def getPlayerByUser(self,name):
        return self.getPlayerByID(await convertNameToId(name))
    
    async def locatePlayer(self, identifier:str):
        #Regex for ubi-id
        if (re.match("[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}", str(identifier))):
            return self.getPlayerByID(identifier)
        
        #General Regex for Ubisoft usernames
        elif (re.match("^[a-zA-Z][-A-Za-z0-9_.]{2,14}$", str(identifier))):
            return await self.getPlayerByUser(identifier)
        
        #Regex for @mention 
        elif (re.match("^(<@)?[0-9]{17,19}(>)?$", str(identifier))):
            if type(identifier) == str:
                identifier = identifier.replace('<', '').replace('>', '').replace('@', '')
            return self.getPlayerByDiscord(identifier)

        else:
            return None, None

    def addPlayer(self, id):
        for x in self.players:
            if x.id == id:
                return
        self.players.append(DBPlayer(id))

    def removePlayer(self, player):
        for x in self.players:
            if x.id == player:
                self.players.remove(x)

    async def refresh(self, api: APIAuth):
        for x in self.players:
            x.update(api)

    def __iter__(self):
        self.i = -1
        return self
    
    def __index__(self, a):
        return self.players[a]
    
    def __next__(self):
        if self.i < len(self.players):
            self.i += 1
            return self.players[self.i]
        else:
            raise StopIteration
        
    def __getitem__(self, a) -> DBPlayer:
        return self.players[a]
    
    def __len__(self) -> int:
        return len(self.players)
    
    def __reduce__(self):
        return (DBRoster, (self.players, ))