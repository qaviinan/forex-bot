from aioskd import Scheduler
from datetime import datetime as dt, timedelta

skd = Scheduler()

async def sub():
    if (round(dt.timestamp(dt.now()),0))%2 == 0:
        myval = 'some string'
        print(myval/2)
    else:
        myval = 'oi mama'
        print(myval/2)

@skd.schedule(interval=timedelta(seconds=5))
async def main():
    attempts = 0
    while attempts <5:
        try:
            await sub()
        except Exception as e:
            print('Oi mama na pls')
            print(e)
            attempts += 1

if __name__ == "__main__":
    # Obligatory test run
    skd.run()