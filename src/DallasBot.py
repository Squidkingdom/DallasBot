from siegeapi import Auth as APIAuth
from threading import Timer
import json
import pickle
import discord
from discord import app_commands
import asyncio
import os
import re
import sys
from datetime import datetime, timedelta
from objects.guild import DBGuild, DBCluster
from objects.player import DBPlayer
from objects.roster import DBRoster, convertNameToId
import os
from siegeapi.exceptions import InvalidRequest


sys.path.append("objects")


class DallasBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dayLog = 7
        self.servers: DBCluster = DBCluster()
        self.tree = app_commands.CommandTree(self)

    def getDBGuild(self, id: int):
        for i in range(len(self.servers)):
            if self.servers[i].id == id:
                return i
        return -1

    async def getEmojiByRankId(self, id=id):
        if (id <= 5):
            return "<:CopperRank:1088720187496341525>"
        if (id <= 10):
            return "<:BronzeRank:1088720191686459402>"
        if (id <= 15):
            return "<:SilverRank:1088722565494755348>"
        if (id <= 20):
            return "<:GoldRank:1088720190931488798>"
        if (id <= 25):
            return "<:PlatinumRank:1088720186711998474>"
        if (id <= 30):
            return "<:EmeraldRank:1088723917750935592>"
        if (id <= 35):
            return "<:DiamondRank:1088720189161488424>"
        else:
            return "<:ChampRank:1088720190147133480>"

    async def genMessage(self, guild: DBGuild):
        now = datetime.now()
        auth = APIAuth(token='U3F1aWRkeXR3ZWFrc0BnbWFpbC5jb206SmF5aGF3ayoy')
        print(f"Last updated: {now}")
        msg = ""
        roster = guild.roster

        global db  # J                                       D                                      T                                      B                                       D                                       K
        # make sure file exists if not create it
        if not os.path.exists("./data/data-" + str(guild.id)):
            db = open("./data/data-" + str(guild.id), 'w+', encoding='UTF-8')
            db.write("")
            db.close()
        db = open("./data/data-" + str(guild.id), 'r+', encoding='UTF-8')
        contents = db.read()
        db.seek(0, 0)
        fileData = []
        dbMsg = ""
        # needs to be removed, but require DB intervention
        for line in db:
            fileData.append(json.loads(line.replace("\'", "\"")))
        if roster == [] or len(roster) == 0:
            msg += "No players in roster. Try !addplayers\n"  # short circuts the for loop

        for i in range(len(roster)):
            member = roster.__index__(i)
            apiData = await auth.get_player(uid=member.id)
            await apiData.load_ranked_v2()
            self.servers[guild.id].roster.__index__(i).name = apiData.name

            dbData = dict
            # TODO JSON dump this to remove line 1212
            dbData = json.dumps({
                "id": member.id,
                "totalGames": apiData.ranked_profile.wins + apiData.ranked_profile.losses,
                "totalKills":  apiData.ranked_profile.kills,
                "totalDeaths": apiData.ranked_profile.deaths,
                "time": (datetime.now() - datetime(1970, 1, 1)).total_seconds()
            })
            dbMsg += str(dbData) + "\n"
            deltaK = 0
            deltaD = 1
            deltaG = 0
            for j in range(len(fileData)):
                if fileData[j]["id"] != member.id:
                    continue
                if fileData[j]["time"] < ((datetime.now() - datetime(1970, 1, 1)).total_seconds() - timedelta(days=member.rollingBounds).total_seconds()):
                    break
                else:
                    deltaK = (apiData.ranked_profile.kills -
                              fileData[j]["totalKills"])
                    deltaD = (apiData.ranked_profile.deaths -
                              fileData[j]["totalDeaths"])
                    deltaG = (apiData.ranked_profile.wins +
                              apiData.ranked_profile.losses) - fileData[j]["totalGames"]


            msg += str(f"__**Name**__: {await self.getEmojiByRankId(apiData.ranked_profile.rank_id)} {apiData.name}\n")
            msg += str(f"__**Rank**__:  *{apiData.ranked_profile.rank}*\n")
            msg += str(
                f"**__Ranked Games__**: {apiData.ranked_profile.wins + apiData.ranked_profile.losses} ({deltaG})\n")
            msg += str(f"**__Rolling KD__**: {round(ndigits=2, number=(deltaK/deltaD if deltaD != 0 else 0))} ({round(ndigits=2, number=(apiData.ranked_profile.kills/apiData.ranked_profile.deaths))}) \n")
            msg += "\n"

        if guild.id == 898691030059200552:
            apiData = await auth.get_player(uid='c22ceb97-8f6d-44f5-9247-90552f610722')
            await apiData.load_ranked_v2()
            msg += str(
                f"<:SilverIVRank:1090146323333906462> Ryan's KD: {apiData.ranked_profile.kills/apiData.ranked_profile.deaths-0.04}\n\n")

        lastUpdate = f"Last updated: {now.strftime('%-m/%-d').strip('0')} {now.strftime('%-I')}:{now.strftime('%M')}{now.strftime('%p').lower()} "
        msg += f"{lastUpdate}\n\n"

        db.seek(0)
        db.write(dbMsg + contents)
        db.close()

        await auth.close()
        return msg

    async def reset(self, guild: DBGuild):
        # TODO add error handing
        i = 0
        dbi = self.getDBGuild(guild.id)
        server = self.get_guild(guild.id)
        if (guild.dispChannel == None):
            return # TODO responds ephemerally
        for j, channel in enumerate(server.text_channels):
            if (channel.id == guild.dispChannel):
                i = j
        await server.text_channels[i].purge()
        msg = await self.genMessage(guild)

        msg = await server.text_channels[i].send(str(msg))
        self.servers[dbi].displayMsg = msg.id
        await msg.add_reaction("🔄")

    async def update(self, guild: DBGuild):

        if (guild.dispChannel == None):
            return

        if (guild.displayMsg == 0):
            await self.reset(guild)
        else:
            i = 0
            dbi = self.getDBGuild(guild.id)
            server = self.get_guild(guild.id)
            for j, channel in enumerate(server.text_channels):
                if (channel.id == guild.dispChannel):
                    i = j
            try:
                msg = await server.text_channels[i].fetch_message(guild.displayMsg)
            except discord.errors.NotFound:
                await self.reset(guild)
                return
            await msg.edit(content=await self.genMessage(guild))
            await msg.add_reaction("🔄")

    async def clientTick(self):
        self.saveGuilds()
        await asyncio.sleep(delay=43200)
        await self.clientTick()

    async def on_raw_reaction_add(self, payload=discord.RawReactionActionEvent):
        dGuild = self.servers[self.getDBGuild(payload.guild_id)]
        if (payload.message_id == dGuild.displayMsg):
            for channel in self.get_guild(payload.guild_id).text_channels:
                if (channel.id == dGuild.dispChannel):
                    if (payload.member != self.get_guild(payload.guild_id).me):
                        msg = await channel.fetch_message(dGuild.displayMsg)
                        await msg.remove_reaction(member=payload.member, emoji=payload.emoji)
                        await self.update(dGuild)
                        return

    async def on_ready(self):
        print(f'We have logged in as {self.user}')
        # await self.loadGuilds()
        self.tree.copy_global_to(guild=discord.Object(id=867340240581558282))
        await self.tree.sync(guild=discord.Object(id=867340240581558282))
        await self.loadGuilds()
        # tree.copy_global_to(guild=discord.Object(id=867340240581558282))
        if len(self.servers) > len(self.guilds):
            self.cleanCluster()
            self.saveGuilds()
        await self.clientTick()

    def cleanCluster(self):
        for server in self.servers:
            for guild in self.guilds:
                if server.id == guild.id:
                    break
                self.servers.remove(server)
        self.saveGuilds()

    def saveGuilds(self):
        # verify that a guild.gb file exists
        pickle.dump(self.servers, open(f"./data/persistence/guilds.db", "wb"))
        # for every guild the bot is in, save the guild data

    async def loadGuilds(self):
        # verify that a guilds folder exists
        if not os.path.exists("./data/persistence/guilds.db"):
            print(f"Creating guilds.db")
            for guild in self.guilds:
                self.servers.append(DBGuild(guild=guild))
            self.saveGuilds()
            print("Created guilds.db")
            return
        print(f"Loading... ")
        self.servers = (pickle.load(
            open("./data/persistence/guilds.db", "rb")))
        print(f"Loaded")

        return True
        # for every file in the guilds folder, load the guild data

    async def on_guild_join(self, guild):
        newGuild = DBGuild(guild=guild)
        for server in self.servers:
            if server.id == newGuild.id:
                return
        self.servers.append(newGuild)
        await newGuild.guild.system_channel.send("Please type !bind cmd/display to bind the bot to a command channel and a display channel.")

    async def on_guild_remove(self, guild):
        # We wrote general code for this earlier
        self.cleanCluster()

    
    #waxed
    

    async def on_message(self, message=discord.Message):
        if message.author == self.user:
            return

        if message.content.startswith('!help'):
            await message.channel.send('Commands are !update, !reset, !help, !purgechannel, !addplayer [player-id], !removeplayer [player-id], !bind cmd, !bind display, !setUbi [player-id|player-name]')
        if message.content.startswith('!res'):
            await self.reset(self.servers[message.guild.id])
        if message.content.startswith('!u'):
            await self.update()
        if message.content.startswith('!p'):
            await message.channel.purge()
            await message.channel.send('Commands are !update, !reset, !help, !purgechannel')
        if message.content.startswith('!add'):
            gid = message.guild.id
            # if matches regex "[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}"gm
            if (re.match("[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}", message.content.split()[1])):
                id = message.content.split()[1]
            else:
                id = await convertNameToId(message.content.split()[1])
            self.servers[gid].roster.addPlayer(id)
            # self.saveGuilds()
            await self.update(self.servers[gid])
        if message.content.startswith('!rem'):
            if (re.match("[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}", message.content.split()[1])):
                id = message.content.split()[1]
            else:
                id = await convertNameToId(message.content.split()[1])
            self.servers[message.guild.id].roster.removePlayer(id)
            await self.update(self.servers[message.guild.id])
        if message.content.startswith('!bind'):
            if message.content.split()[1] == 'cmd':
                i = self.getDBGuild(message.guild.id)
                self.servers[i].cmdChannel = message.channel.id
                message.channel.send(
                    f"Set command channel to *{message.channel.name}*")
            if message.content.split()[1] == 'display':
                i = self.getDBGuild(message.guild.id)
                self.servers[i].dispChannel = message.channel.id
                await message.channel.send(f"Set display channel to *{message.channel.name}*")
                await self.reset(self.servers[i])
        if message.content.startswith('!save'):
            self.saveGuilds()
        if message.content.startswith('!link'):
            for i, player in enumerate(self.servers[message.guild.id].roster.players):
                if len(message.content.split()) == 1:
                    await message.channel.send(f"Usage is !link <ubi-id|ubi-name> [discord-id]")
                    break
                gid = message.guild.id
                # set or convert id
                if (re.match("[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}", message.content.split()[1])):
                    id = message.content.split()[1]
                else:
                    id = await convertNameToId(message.content.split()[1])

                if player.id == id:
                    # TODO, might not be safe
                    if len(message.content.split()) > 2:
                        discordID = int(message.content.split()[2].replace('<', '').replace('>', '').replace('@', ''))
                    
                    else:
                        discordID = int(message.author.id)

                    pn = message.guild.get_member(discordID).display_name

                    if player.discordID != None:
                        await message.channel.send(f"That player is already linked with {pn}")
                        break

                    i =  self.servers[message.guild.id].roster.players.index(player)
                    
                    self.servers[gid].roster.players[i].discordID = int(discordID)
                        
                    await message.channel.send(f"Set linked discord account to {pn}")
                    break
            else:
                await message.channel.send(f"Roster member not found!")
        if message.content.startswith('!setRB'):
            if len(message.content.split()) == 1:
                await message.channel.send("Usage: !setRB <bounds> [@discord-id | Ubi-Username | Ubi-id]")
                return

            newBounds = int(message.content.split()[1])
            gid = message.guild.id

            if len(message.content.split()) == 2:
                id = message.author.id
            elif len(message.content.split()) == 3:
                id = message.content.split()[2]
            
            i = (await self.servers[gid].roster.locatePlayer(id))[0]

            if i == None:
                await message.channel.send(f"Roster member not found!\n"
                                           f"Please link accounts with !link <ubi-id> [@discord-id]")
                return
            
            self.servers[gid].roster.players[i].rollingBounds = newBounds
            await message.channel.send(f"Set rolling bounds to {newBounds} for {self.servers[gid].roster.players[i].name}")
            return
        if message.content.startswith('!whatRB'):
            gid = message.guild.id
            if len(message.content.split()) == 1:
                id = message.author.id
            else:
                id = message.content.split()[1]
            
            i = (await self.servers[gid].roster.locatePlayer(id))[0]
            if i == None:
                await message.channel.send(f"Roster member not found! Please link accounts with !link <Ubi-id | Ubi-Username> [@discord-id]")
                return
            await message.channel.send(f"Rolling bounds for {self.servers[gid].roster.players[i].name} are {self.servers[gid].roster.players[i].rollingBounds}")


# class TaskScheduler:
#     self.timer = Timer(30.0, )



# if __name__ == "__main__":
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

dal = DallasBot(intents=intents)

@dal.tree.command(name = "ping", description = "Ping Command")
async def ping(ctx: discord.interactions.Interaction):
      await ctx.response.send_message("Pong!", ephemeral = True)

try:
    # dal.run(open('tokens/token.prod', 'r', encoding='utf-8').read())
    dal.run(open('./data/tokens/token.beta', 'r', encoding='utf-8').read())
except Exception as e:
    print(e)
