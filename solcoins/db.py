import env
import sqlite3

database = sqlite3.connect(f'data/{env.DATABASE_NAME}')


def bootstrap():
    print("Bootstrapping database...")
    _get_cursor().execute("CREATE TABLE IF NOT EXISTS watchlist(guild_id, channel_id, name, address)")


def get():
    return _get_cursor().execute('SELECT guild_id, channel_id, address from watchlist').fetchall()


def delete(channel):
    print(f'Deleting channel...\nguild_id: {channel.guild.id}\nchannel_id: {channel.id}')
    _get_cursor().execute("DELETE FROM watchlist WHERE guild_id=:guild_id and channel_id=:channel_id",
                          {'guild_id': channel.guild.id, 'channel_id': channel.id})
    database.commit()


def save(guild_id, channel_id, name, address):
    print(f'Adding to guild (id: {guild_id}) watchlist (name: {name} - contract_address: {address})')
    _get_cursor().execute("INSERT INTO watchlist VALUES (:guild_id, :channel_id, :name, :address)",
                          {'guild_id': guild_id, 'channel_id': channel_id, 'name': name, 'address': address})
    database.commit()


def _get_cursor():
    return database.cursor()
