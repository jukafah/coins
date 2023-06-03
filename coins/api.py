from solcoins import env
import aiohttp


# todo: error handling
async def get_price(address: str):
    async with aiohttp.ClientSession() as session:
        request = f'{env.API_URL}/price?address={address}'
        print(f"Sending request: {request}")
        async with session.get(request) as response:
            return await response.json()
    # return {
    #     "data": {
    #         "value": 0.0004473968660744325,
    #         "updateUnixTime": 1676210308,
    #         "updateHumanTime": "2023-02-12T13:58:28"
    #     },
    #     "success": True
    # }


# todo: error handling
async def get_multi_price(addresses: str):
    async with aiohttp.ClientSession() as session:
        request = f"{env.API_URL}/multi_price?list_address={addresses}"
        print(f"Sending request: {request}")
        async with session.get(request) as response:
            return await response.json()
    # return {
    #     "data": {
    #         "F9CpWoyeBJfoRB8f2pBe2ZNPbPsEE76mWZWme3StsvHK": {
    #             "value": 0.0002475065678021732,
    #             "updateUnixTime": 1676210288,
    #             "updateHumanTime": "2023-02-12T13:58:08",
    #             "priceChange24h": 9.029513553793803
    #         },
    #         "32RdXYmiHbmfVpCTJ8dcjDMGShHkjcoTWYf1QtMb5ZDT": {
    #             "value": 0.000123273248638588024,
    #             "updateUnixTime": 1676220413,
    #             "updateHumanTime": "2023-02-12T16:46:53",
    #             "priceChange24h": 319.2046976709038
    #         }
    #     },
    #     "success": True
    # }
