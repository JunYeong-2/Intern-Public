import aiohttp
import asyncio
import json
import logging

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

async def put(url1, data, headers):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.put(url1, data=json.dumps(data), headers=headers) as r:
                if r.status != 200:
                    LOGGER.info(r.status)
                else:
                    LOGGER.info("Transmission success!")
    except aiohttp.ClientTimeout(total=60) as errd:
        LOGGER.exception("Timeout Error: %s", errd)
    except aiohttp.ClientConnectionError as errc:
        LOGGER.exception("Error Connecting: %s", errc) 
    except aiohttp.ClientHttpProxyError as errb:
        LOGGER.exception("HTTP Error: %s", errb)
    except aiohttp.ClientError as erra:
        LOGGER.exception("Any Exception: %s", erra)


async def get(url1):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url1) as r:
                if r.status != 200:
                    LOGGER.info("HTTP Error code: %s", r.status)
                return r
    except aiohttp.ClientTimeout(total=300) as err:
        LOGGER.exception("Timeout Error: %s", err)
    except aiohttp.ClientConnectionError as err:
        LOGGER.exception("Error Connecting: %s", err)
    except aiohttp.ClientResponseError as err:
        LOGGER.exception("HTTP Error: %s", err)
    except aiohttp.ClientError as err:
        LOGGER.exception("Any Exception: %s", err)

async def main1(url, data, headers):
    await put(url, data, headers)

async def main2(url):
    await get(url)

async def run_main1(url, data, headers):
    await main1(url, data, headers)

async def run_main2(url):
    await main2(url)

url = 'https://www.naver.com'
data = [1,2,3]
headers = {'hello' : 'hello2'}

async def run_program():
    await run_main1(url, data, headers)
    await run_main2(url)

asyncio.run(run_program())
