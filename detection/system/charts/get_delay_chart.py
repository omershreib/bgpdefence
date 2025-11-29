from config import CONFIG
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure


def get_data_plane_delay(data_plane):
    for hop in data_plane['hops'][::-1]:
        if hop['responded']:
            return min([delay for delay in hop['delays'] if delay is not None])

    return 0

def set_delay_scatter():
    fig = Figure()
    ax = fig.subplots()
    scat = ax.scatter([], [], c='blue')
    ax.set_title('Traceroute Delay Over Time')
    ax.set_xlabel('Time')
    ax.set_ylabel('Delay (ms)')
    ax.grid(True)

    return fig, ax


def get_delay_chart(collection):
    """
    Get Delay Chart

    Note:
    ----
    the number of last points (limit) and delay threshold value can be configured in the config file

    :param collection: mongoDB MongoClient object (should equal to db['traceroutes'])
    :return: matplotlib chart figure
    """
    limit = CONFIG['dashboard']['delay_points_limit']
    threshold = CONFIG['dashboard']['delay_points_threshold']

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

    plt.style.use('dark_background')

    fig, ax = set_delay_scatter()
    times = [t for t, _ in delay_data]
    delays = [d for _, d in delay_data]

    times.reverse()
    delays.reverse()

    # matplotlib
    plt.scatter(times, delays, color=['blue' if delay < threshold else 'red' for delay in delays])
    plt.plot(times, delays, linestyle='--', color='red', label='Dashed Line')
    plt.xticks(rotation=45)
    plt.title(f"Delay Timeline (Last {limit} Probes)")

    plt.tight_layout()
    return fig
