import os
import sqlite3
from collections import defaultdict

import aiohttp
import discord
from discord.ext import tasks, commands
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
DATABASE_NAME = os.getenv('DATABASE_NAME')
BIRDEYE_API_KEY = os.getenv('BIRDEYE_API_KEY')

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

database = sqlite3.connect(f'db/{DATABASE_NAME}')


class Watch(commands.Cog):

    # can I save guild here?
    def __init__(self):
        self.update.start()

    def cog_unload(self):
        self.update.cancel()

    @tasks.loop(minutes=5)
    async def update(self):
        cursor = database.cursor()
        watchlists_to_update = cursor.execute('SELECT guild_id, channel_id, address from watchlist').fetchall()
        print(f'watchlists_to_update: {watchlists_to_update}')

        formatted = defaultdict(list)

        """
        {
          "983794691914989619": [
            {"channel_id": "1074450604576997467", "address": "32RdXYmiHbmfVpCTJ8dcjDMGShHkjcoTWYf1QtMb5ZDT"},
            {"channel_id": "1074451330766209056", "address": "F9CpWoyeBJfoRB8f2pBe2ZNPbPsEE76mWZWme3StsvHK"},
          ]
        }
        """
        for watching in watchlists_to_update:
            formatted[watching[0]].append({'channel_id': watching[1], 'address': watching[2]})

        for guild in client.guilds:
            print(f'guild: {guild} (guild_id: {guild.id})')
            print(f'watchlist to update: {formatted[guild.id]}')
            addresses = [key['address'] for key in formatted[guild.id]]
            print(f'addresses: {addresses}')
            updated_prices = await get_price(",".join(addresses))
            for item in formatted[guild.id]:
                channel_id = item['channel_id']
                address = item['address']
                print(f"channel_id: {channel_id}\naddress: {address}")
                channel = discord.utils.get(guild.voice_channels, id=channel_id)
                split_name = channel.name.split('@')
                split_name[1] = str(updated_prices['data'][address]['value'])
                await channel.edit(name="@ ".join(split_name))


def bootstrap():
    cursor = database.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS watchlist(guild_id, channel_id, name, address)")


@client.event
async def on_ready():
    print(f"client.guilds: {client.guilds}")
    guild = discord.utils.get(client.guilds, name=GUILD)
    bootstrap()
    Watch()
    await tree.sync()
    print(f'{client.user} is connected to guild: {guild.name}(id: {guild.id})')


@client.event
async def on_guild_channel_delete(channel):
    print(f"channel.id: {channel.id}")
    print(f'Deleting channel...\nguild_id: {channel.guild.id}\nchannel_id: {channel.id}')
    cursor = database.cursor()
    cursor.execute("DELETE FROM watchlist WHERE guild_id=:guild_id and channel_id=:channel_id", {'guild_id': channel.guild.id, 'channel_id': channel.id})
    database.commit()


async def get_price(address):
    return {
        "data": {
            "F9CpWoyeBJfoRB8f2pBe2ZNPbPsEE76mWZWme3StsvHK": {
                "value": 0.0002475065678021732,
                "updateUnixTime": 1676210288,
                "updateHumanTime": "2023-02-12T13:58:08",
                "priceChange24h": 9.029513553793803
            },
            "32RdXYmiHbmfVpCTJ8dcjDMGShHkjcoTWYf1QtMb5ZDT": {
                "value": 0.000123273248638588024,
                "updateUnixTime": 1676220413,
                "updateHumanTime": "2023-02-12T16:46:53",
                "priceChange24h": 319.2046976709038
            }
        },
        "success": True
    }
    # async with aiohttp.ClientSession(headers={"X-API-KEY": BIRDEYE_API_KEY}) as session:
    #     async with session.get(f'https://public-api.birdeye.so/public/multi_price?list_address={address}') as r:
    #         return await r.json()


@tree.command(name='watchlist', description='Add a coin to your watchlist by contract address')
async def add_to_watchlist(ctx, name: str = '', address: str = ''):
    print(f'Adding to watchlist\nname: {name}\ncontract_address: {address}')
    cursor = database.cursor()
    price = await get_price(address)
    value = price['data'][address]['value']
    created_channel = await ctx.guild.create_voice_channel(name=f'{name} @ {str(value)[:8]}', position=0)
    cursor.execute("INSERT INTO watchlist VALUES (:guild_id, :channel_id, :name, :address)", {'guild_id': ctx.guild.id, 'channel_id': created_channel.id, 'name': name, 'address': address})
    database.commit()


client.run(TOKEN)
