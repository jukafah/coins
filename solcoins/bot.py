import env
import db

import discord
import api
from cogs import UpdateWatchlists

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)


@client.event
async def on_ready():
    db.bootstrap()
    UpdateWatchlists(api=api, db=db, client=client)
    await tree.sync()


@client.event
async def on_guild_channel_delete(channel):
    db.delete(channel)


@tree.command(name='watchlist', description='Add a coin to your watchlist by contract address')
async def add_to_watchlist(ctx, name: str = '', address: str = ''):
    print(f'Adding to watchlist\nname: {name}\ncontract_address: {address}')
    price = await api.get_price(address)
    channel = await ctx.guild.create_voice_channel(name=f"{name} @ {str(price['data']['value'])[:8]}", position=0)
    db.save(ctx.guild.id, channel.id, name, address)


client.run(env.TOKEN)
