import sys
import discord
sys.path.append('.')
from objects.roster import DBRoster
class DBGuild:
    def __init__(self, id=None, cmd=None, dispChannel = None, roster:DBRoster = DBRoster(), dispMsg=None, guild:discord.Guild = None):
        self.id = guild.id if guild != None else id
        self.cmdChannel = cmd
        self.dispChannel = dispChannel
        self.displayMsg = dispMsg
        self.roster = roster
    def __reduce__(self):
        return (DBGuild, (self.id, self.cmdChannel, self.dispChannel,self.roster, self.displayMsg))

    
class DBCluster:
    def __init__(self, guilds = []):
        self.guilds = guilds

    def __len__(self) -> int:
        return len(self.guilds)

    def __getitem__(self, a) -> DBGuild:
        if type(a) == DBGuild:
            for i in range(len(self.guilds)):
                if self.guilds[i].id == a.id:
                    return self.guilds[i]
        if a > 100:
            for i in range(len(self.guilds)):
                if self.guilds[i].id == a:
                    return self.guilds[i]
        else:
            return self.guilds[a]

    def append(self, guild: DBGuild):
        if len(self.guilds) == 0:
            self.guilds.append(guild)
            return
        for i in range(len(self.guilds)):
            if self.guilds[i].id == guild.id:
                self.guilds[i] = guild
                break
            self.guilds.append(guild)

    def remove(self, guild: DBGuild):
        for i in range(len(self.guilds)):
            if self.guilds[i].id == guild.id:
                self.guilds.remove(guild)
                break

    def __reduce__(self):
        return (DBCluster, (self.guilds,))