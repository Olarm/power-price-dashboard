import requests
import datetime
import json
from entsoe import EntsoePandasClient
import pandas as pd

from secrets.py import *

country_code = 'NO_3'
supplier = "tibber"

def get_eur_nok_conversion():
    response = requests.get("https://v6.exchangerate-api.com/v6/7a99eaacea7351a0dbbb09af/latest/eur")
    if response.ok:
        body_json = response.json()
        rates = body_json.get("conversion_rates")
        nok = rates.get("NOK")
        return nok


def get_day_ahead():
    client = EntsoePandasClient(api_key=ENTSOE_TOKEN)
    start = pd.Timestamp(datetime.date.today(), tz="Europe/Oslo")
    end = pd.Timestamp(datetime.date.today() + datetime.timedelta(days=3), tz="Europe/Oslo")
    data = client.query_day_ahead_prices(country_code, start=start, end=end)

    nok_eur = get_eur_nok_conversion()
    data *= nok_eur
    data *= 1e-1    # øre per kWh
    if supplier == "tibber":
        data += 1.0     # paslag 1.0 øre/kWh
    elif supplier == "lyse":
        data += 3.2     # paslag 3.2 øre/kWh
    data *= 1.25    # moms 25%

    df = pd.DataFrame({'time':data.index, 'price':data.values})
    return df
