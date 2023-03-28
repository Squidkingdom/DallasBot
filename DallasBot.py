from siegeapi import Auth
from threading import Timer
import json
import discord
import asyncio
import os
from datetime import datetime, timedelta

class DallasBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.displayMsgId = 1090174727290638367
        self.dayLog = 7

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

    async def genMessage(self):
        now = datetime.now()
    
        print(f"Last updated: {now}")
        msg = ""
        

        global db  # J                                       D                                      T                                      B                                       D                                       K
        urls = ['764d1468-e26d-4417-8789-902b352b6bb7', '1869520c-5556-4178-93ea-fe92fff0d3ee', 'f765dca9-7ed6-4f2e-98ae-7002d58151b4',
                '5eea2a4f-fa30-4db8-a087-89480b5af852', '1a8ba3a9-fe66-4346-bbb6-3daa82005e25', 'bcffb8cd-af5d-4b60-bbfb-8bb0dac56257']
        recentData = [[], [], [], [], [], []]
        
        auth = Auth("Squiddytweaks@gmail.com", "Jayhawk*2")
        db = open("data", 'r+', encoding='UTF-8')
        contents = db.read()
        db.seek(0, 0)
        fileData = []
        dbMsg = ""

        for line in db:
            fileData.append(json.loads(line.replace("\'", "\"")))

        for i in range(len(urls)):
            player = await auth.get_player(uid=urls[i])
            await player.load_ranked_v2()
            data = dict
            data = {
                "id": urls[i],
                "totalGames": player.ranked_profile.wins + player.ranked_profile.losses,
                "totalKills":  player.ranked_profile.kills,
                "totalDeaths": player.ranked_profile.deaths,
                "time": (datetime.now() - datetime(1970, 1, 1)).total_seconds()
            }
            dbMsg += str(data) + "\n"

            for j in range(len(fileData)//len(urls)):
                if fileData[(j*len(urls)) + i]["time"] < ((datetime.now() - datetime(1970, 1, 1)).total_seconds() - timedelta(days=self.dayLog).total_seconds()):
                    break
                else:
                    deltaK = (player.ranked_profile.kills - fileData[(j*len(urls)) + i]["totalKills"])
                    deltaD = (player.ranked_profile.deaths - fileData[(j*len(urls)) + i]["totalDeaths"])
                    deltaG = (player.ranked_profile.wins + player.ranked_profile.losses) - fileData[(j*len(urls)) + i]["totalGames"]

            msg += str(f"__**Name**__: {await self.getEmojiByRankId(player.ranked_profile.rank_id)} {player.name}\n")
            msg += str(f"__**Rank**__:  *{player.ranked_profile.rank}*\n")
            msg += str(f"**__Ranked Games__**: {player.ranked_profile.wins + player.ranked_profile.losses} ({deltaG})\n")
            msg += str(f"**__Rolling KD__**: {round(ndigits=2, number=(deltaK/deltaD if deltaD != 0 else 0))} ({round(ndigits=2, number=(player.ranked_profile.kills/player.ranked_profile.deaths))}) \n")
            msg += "\n"

        player = await auth.get_player(uid='c22ceb97-8f6d-44f5-9247-90552f610722')
        await player.load_ranked_v2()
        db.seek(0)
        db.write(dbMsg + contents)
        db.close()
        msg += str(f"<:SilverIVRank:1090146323333906462> Ryan's KD: {player.ranked_profile.kills/player.ranked_profile.deaths-0.04}\n\n")

        lastUpdate = f"Last updated: {now.strftime('%m/%d').strip('0')} {now.strftime('%I').strip('0')}:{now.strftime('%M')}{now.strftime('%p').lower()} "
        msg += f"{lastUpdate}\n\n"
        await auth.close()
        return msg


    async def reset(self):
        await self.guilds[0].text_channels[2].purge()
        msg = await self.genMessage()
        msg = await self.guilds[0].text_channels[2].send(msg)
        await msg.add_reaction("🔄")
        self.displayMsgId = msg.id


    async def update(self, repeat=False, delaySeconds=43200):
        if (self.displayMsgId == 0):
            await self.reset()
        else:
            msg = await self.guilds[0].text_channels[2].fetch_message(self.displayMsgId)
            await msg.edit(content=await self.genMessage())
            await msg.add_reaction("🔄")
        while (repeat):
            await asyncio.sleep(delay=delaySeconds)
            await self.update()


    async def clientTick(self):
        await self.update(repeat=True, delaySeconds=43200)

  
    async def on_raw_reaction_add(self, payload = discord.RawReactionActionEvent):
        msg = await self.get_guild(payload.guild_id).text_channels[2].fetch_message(self.displayMsgId)
        await msg.remove_reaction(member=payload.member, emoji=payload.emoji)
        
        if ((payload.message_id == self.displayMsgId) and payload.emoji.name == '🔄'):
            if (payload.member != self.get_guild(payload.guild_id).me):
                
                await self.update()
                
    async def on_ready(self):
        print(f'We have logged in as {self.user}')
        await self.clientTick()


    
    async def on_message(self,message=discord.Message):
        if message.author == self.user:
            return

        if message.channel.id == 1088582317066428496:
            if message.content.startswith('!help'):
                await message.channel.send('Commands are !update, !reset, !help, !purgechannel')
            if message.content.startswith('!r'):
                await self.reset()
            if message.content.startswith('!u'):
                await self.update()
            if message.content.startswith('!p'):
                await message.channel.purge()
                await message.channel.send('Commands are !update, !reset, !help, !purgechannel')


# class TaskScheduler:
#     self.timer = Timer(30.0, )
intents = discord.Intents.default()
intents.message_content = True

dal = DallasBot(intents = intents)


dal.run(open('token', 'r', encoding='utf-8' ).read())
