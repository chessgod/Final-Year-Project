import requests;
import datetime;
import time;
import pandas;
import time;

def apiData(lat, long, timeVal):
    # print(type(timeVal))
    # if(timestamp[:-5] != "00:00"):
    #     timestamp = toUTC(timestamp)
    # timeVal = timeVal.to_pydatetime()
    # unixTime = datetime.datetime(timeVal)
    # unixTime = time.mktime(timeVal.timetuple())
    lat = round(lat,4)
    long = round(long,4)
    print(lat)
    print(long)
    timeVal = timeVal.date()
    response = requests.get(
        f"""https://archive-api.open-meteo.com/v1/archive?latitude={float(lat)}&longitude={float(long)}
        &start_date={timeVal}&end_date={timeVal}&hourly=windspeed_10m,winddirection_100m,windgusts_10m"""
    )
    print(response.text)
    if(response.status_code == 200):
        print(response.json)
