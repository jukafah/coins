from collections import defaultdict
from decimal import Decimal
import discord
from discord.ext import tasks, commands


class UpdateWatchlists(commands.Cog):
    def __init__(self, db, client, api):
        self.update.start()
        self.db = db
        self.client = client
        self.api = api

    def cog_unload(self):
        self.update.cancel()

    @tasks.loop(minutes=5)
    async def update(self):
        unique_addresses = [i[0] for i in self.db.get_unique_addresses()]
        print(f"unique_addresses: {unique_addresses}")
        if not unique_addresses:
            return

        updated_prices = await self.api.get_multi_price(",".join(unique_addresses))
        watchlists = _format_watchlist_for_updates(self.db.get())

        for guild in self.client.guilds:
            for item in watchlists[guild.id]:
                channel_id = item['channel_id']
                address = item['address']

                # todo: need to handle if guild deletes voice channel when down and throws error
                channel = discord.utils.get(guild.voice_channels, id=channel_id)
                split_name = channel.name.split('@')
                updated_price = str(Decimal(updated_prices['data'][address]['value']))[:8]
                split_name[1] = updated_price
                print(f'Updating guild (id: {guild.id}) watchlist (channel_id: {channel.id} - address: {address}) with new price - price: {updated_price}')
                await channel.edit(name="@ ".join(split_name))


def _format_watchlist_for_updates(watchlists):
    """
    {
      "983794691914989619": [
        {"channel_id": "1074450604576997467", "address": "32RdXYmiHbmfVpCTJ8dcjDMGShHkjcoTWYf1QtMb5ZDT"},
        {"channel_id": "1074451330766209056", "address": "F9CpWoyeBJfoRB8f2pBe2ZNPbPsEE76mWZWme3StsvHK"},
      ]
    }
    """
    formatted = defaultdict(list)
    for watching in watchlists:
        formatted[watching[0]].append({'channel_id': watching[1], 'address': watching[2]})
    return formatted
