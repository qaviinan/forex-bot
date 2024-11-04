import asyncio
import pandas as pd
import sys
import time
import random
import asyncio
import datetime
from termcolor import colored
from quotexpy import Quotex
from quotexpy.utils import asset_parse
from quotexpy.utils.account_type import AccountType
from quotexpy.utils.candles_period import CandlesPeriod
from quotexpy.utils.operation_type import OperationType
from aioskd import Scheduler

skd = Scheduler()
asset_current = "USDBDT"


def on_pin_code() -> str:
    code = input("Enter the code sent to your email: ")
    return code


client = Quotex(
    email="qaviinan@gmail.com",
    password="qoutexpass4567",
    headless=True,
    on_pin_code=on_pin_code,
)

def get_filename(df):
    """
    Generates a filename based on the candles data.

    Args:
        candles: List of candle data.

    Returns:
        Filename in the format "bdt-DDYY-last_time-first_time.csv".
    """
    last_time = df.index.max().strftime('%H%M')
    first_time = df.index.min().strftime('%H%M')
    date = datetime.datetime.now().strftime('%d%y')
    return f"bdt-{date}-{last_time}-{first_time}.csv"

def check_asset(asset):
    asset_query = asset_parse(asset)
    asset_open = client.check_asset(asset_query)
    if not asset_open or not asset_open[2]:
        print(colored("[WARN]: ", "yellow"), "Asset is closed.")
        asset = f"{asset}_otc"
        print(colored("[WARN]: ", "yellow"), "Try OTC Asset -> " + asset)
        asset_query = asset_parse(asset)
        asset_open = client.check_asset(asset_query)
    return asset, asset_open

async def get_candle_v2():
    check_connect = await client.connect()
    if check_connect:
        print('connected...')
        global asset_current
        asset, asset_open = check_asset(asset_current)
        if asset_open[2]:
            print(colored("[INFO]: ", "blue"), "Asset is open.")
            candles = await client.get_candle_v2(asset, CandlesPeriod.ONE_MINUTE)
            return candles
        else:
            print(colored("[INFO]: ", "blue"), "Asset is closed.")
    client.close()

async def get_and_save_candles():
    candles = await get_candle_v2() 
    print("here are the candles:", candles)
    df = pd.DataFrame(candles)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)
    df.index = df.index.tz_localize('UTC').tz_convert('Asia/Dhaka')
    filename = get_filename(df)
    df.to_csv(f"data/{filename}")

@skd.schedule(interval=datetime.timedelta(hours=2))
async def main():
    attempts = 0
    while attempts<5:
        try:
            await get_and_save_candles()
            break
        except Exception as e:  # Replace with the specific exception you are expecting
            print('Encountered exception!!!')
            print(e)
            wait = (2 ** attempts) + random.random()  # incremental backoff + jitter
            attempts += 1
            print(f"Waiting {wait:.2f} seconds before trying again.")
            await asyncio.sleep(wait)

if __name__ == "__main__":
    asyncio.run(get_and_save_candles())
    print(f'Starting new get_candles session at time {datetime.datetime.now()}')
    skd.run()