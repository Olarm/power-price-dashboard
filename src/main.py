import requests
import datetime
import json
from entsoe import EntsoePandasClient
import pandas as pd

import logging
from sys import stdout

# Define logger
logger = logging.getLogger('power_price')

logger.setLevel(logging.DEBUG) # set logger level
logFormatter = logging.Formatter\
("%(name)-12s %(asctime)s %(levelname)-8s %(filename)s:%(funcName)s %(message)s")
consoleHandler = logging.StreamHandler(stdout) #set streamhandler to stdout
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)

from secrets import *

conversion_ts = None
EUR_NOK = None

def get_eur_nok_conversion():
    global EUR_NOK
    global conversion_ts
    logger.info("Getting conversion rate.")
    if EUR_NOK != None and conversion_ts != None:
        if conversion_ts > pd.Timestamp(datetime.date.today() - datetime.timedelta(hours=1), tz="Europe/Oslo"):
            return EUR_NOK

    logger.info("Requesting updated conversion rate.")
    response = requests.get(f"https://v6.exchangerate-api.com/v6/{EXCHANGE_TOKEN}/latest/eur")
    if response.ok:
        body_json = response.json()
        rates = body_json.get("conversion_rates")
        nok = rates.get("NOK")
        EUR_NOK = nok
        conversion_ts = pd.Timestamp(datetime.datetime.now(), tz="Europe/Oslo")
        return nok


def get_zone(client, zone, start, end, supplier):
    data = client.query_day_ahead_prices(zone, start=start, end=end)
    nok_eur = get_eur_nok_conversion()
    data *= nok_eur
    data *= 1e-1    # øre per kWh
    if supplier == "tibber":
        data += 1.0     # paslag 1.0 øre/kWh
    elif supplier == "lyse":
        data += 3.2     # paslag 3.2 øre/kWh
    data *= 1.25    # moms 25%

    zone = [zone] * data.size
    df = pd.DataFrame({"time":data.index, "price":data.values, "zone":zone})
    return df


def get_day_ahead(zones=["NO_2", "NO_3"], supplier="tibber"):
    client = EntsoePandasClient(api_key=ENTSOE_TOKEN)
    start = pd.Timestamp(datetime.date.today(), tz="Europe/Oslo")
    end = pd.Timestamp(datetime.date.today() + datetime.timedelta(days=3), tz="Europe/Oslo")

    df = pd.DataFrame(columns=["time", "price", "zone"])
    for zone in zones:
        temp_df = get_zone(client, zone, start, end, supplier)
        df = pd.concat([df, temp_df])

    return df
