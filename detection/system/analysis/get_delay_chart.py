import time

from detection.system.analysis.get_data_plane_delay import get_data_plane_delay
import io
import base64
from _datetime import datetime
import matplotlib.dates as mdates
import pandas as pd
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

from matplotlib.figure import Figure

#plt.style.use('ggplot')
#plt.style.use('fivethirtyeight')
#plt.style.use('dark_background')

def set_delay_scatter():
    fig = Figure()
    ax = fig.subplots()
    scat = ax.scatter([], [], c='blue')
    ax.set_title('Traceroute Delay Over Time')
    ax.set_xlabel('Time')
    ax.set_ylabel('Delay (ms)')
    ax.grid(True)

    return fig, ax


def get_current_delay(collection):
    print("get current delay")
    #limit = 25
    mongo_filter = {
        'sensor_id': 2
    }
    sort = list({'timestamp': -1}.items())
    latest_traceroute = collection.find_one(
        filter=mongo_filter,
        sort=sort
    )

    latest_delay = get_data_plane_delay(latest_traceroute)
    timestamp = latest_traceroute['timestamp'].strftime("%H:%M:%S")

    return latest_delay, timestamp


def get_delay_chart(collection, limit=25):
    delay_data = []

    mongo_filter = {
        'sensor_id': 2
    }
    sort = list({'timestamp': -1}.items())
    mongo_delay_temp = collection.find(
        filter=mongo_filter,
        sort=sort,
        limit=limit
    )

    for item in mongo_delay_temp:
        pack = (item['timestamp'].strftime("%H:%M:%S"), get_data_plane_delay(item))
        delay_data.append(pack)

    threshold = 150
    #plt.style.use('seaborn-v0_8-dark')
    #plt.style.use('fivethirtyeight')
    plt.style.use('dark_background')

    fig, ax = set_delay_scatter()

    # for t, _ in delay_data:
    #     print(t)

    times = [pd.to_datetime(t) for t, _ in delay_data]
    #times = [datetime.strptime(t, '%H:%M:%S') for t, _ in delay_data]
    #times = [t for t, _ in delay_data]
    delays = [d for _, d in delay_data]

    # # label, value
    # return times, delays

    # matplotlib
    plt.scatter(times, delays, color=['blue' if delay < threshold else 'red' for delay in delays])
    plt.plot(times, delays, linestyle='--', color='red', label='Dashed Line')
    plt.xticks(rotation=45)
    plt.title(f"Delay Timeline (Last {limit} Probes)")

    plt.tight_layout()
    return fig


if __name__ == '__main__':
    from pymongo import MongoClient

    client = MongoClient("mongodb://localhost:27017/")
    db = client["network_monitoring"]
    collection = db['traceroutes']

    fig = get_delay_chart(collection)

    delay_chart_fig = get_delay_chart(collection)
    filename = f"test_delay.png"

    fig.tight_layout()
    plt.savefig(filename, format="png", dpi=120)
    plt.close(fig)
    plt.clf()

