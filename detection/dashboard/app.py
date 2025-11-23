from detection.system.sensor import sensor
from detection.system.database.mongo_inserter import MongoInserter
from detection.system.analysis.get_delay_chart import get_delay_chart, get_current_delay
from detection.system.analysis.get_cplane_chart import get_cplane_chart
from detection.system.analysis.get_dplane_chart import get_dplane_chart
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask import request, Flask, render_template, url_for, render_template_string
from flask_socketio import SocketIO
from turbo_flask import Turbo
from threading import Lock
from datetime import datetime, timedelta
from markupsafe import escape
import threading
from random import random
import time
import os
import pandas as pd
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

# background thread
thread = None
thread_lock = Lock()

# mongodb config
client = MongoClient("mongodb://localhost:27017/")
db = client["network_monitoring"]

# flask config
app = Flask(__name__)
app.config['SERVER_NAME'] = 'BGPDashbard'
# app.config['HOST'] = '192.0.0.3'
app.config['SECRET_KEY'] = 'bgphijack'
turbo = Turbo(app)
#socketio = SocketIO(app, cors_allowed_origins='*')
STATIC_DIR = os.path.join(app.root_path, "static", "charts")
os.makedirs(STATIC_DIR, exist_ok=True)

# prefix2as configs
prefix2as_csv = r"D:\Documents\open university\netSeminar\source\detection\detection_tools\prefix2as.csv"
prefixes = pd.read_csv(prefix2as_csv)


def get_current_datetime():
    now = datetime.now()
    return now.strftime("%m/%d/%Y %H:%M:%S")


def render_data_plane_fragment(state):
    return render_template_string(
        """
            <div class="container mx-auto p-2" style="color: white;">
      <h6 name="uuid" style="text-align: justify;">UUID: {{ data_plane._id }}</h6>
      <h6 style="text-align: justify;">datetime:    {{ data_plane.timestamp }}</h6>
      <h6 style="text-align: justify;">sensorId:    {{ data_plane.sensor_id }}</h6>
      <h6 style="text-align: justify;">destination: {{ data_plane.destination_ip }}</h6>
    </div>
    
    <div class="container">
      <div class="d-grid gap-2 d-md-flex justify-content-md-end" style="margin-bottom: 2%;">
          <a name="btn_previous" onclick="performPost()" class="btn btn-outline-light" style="margin-right: 1%;" type="submit" href="{{ url_for('dashboard', uuid=prev_id) }}">previous</a>
          <a name="btn_next"  onclick="performPost()" class="btn btn-outline-light" type="submit" href="{{ url_for('dashboard', uuid=next_id) }}">next</a>
      </div>
      <div class="table-responsive">
      <table id="data_plane" class="table table-dark table-striped table-hover table-bordered">
          <thead>
            <tr>
              <th scope="col">#</th>
              <th scope="col"></th>
              <th scope="col"></th>
              <th scope="col"></th>
              <th scope="col">IP</th>
              <th scope="col">ASN</th>
            </tr>
          </thead>
          <tbody>
            {% for hop in data_plane.hops %}
              <tr>
                <td>{{ hop.hop_num }}</td>
                  {% if hop.delays[0] %}
                <td>{{ hop.delays[0] | round | int if hop.delays[0] else '*' }}ms</td>
                  {% else %}
                <td> * </td>
                  {% endif %}
    
                  {% if hop.delays[1] %}
                <td>{{ hop.delays[1] | round | int if hop.delays[0] else '*' }}ms</td>
                  {% else %}
                <td> * </td>
                  {% endif %}
                  {% if hop.delays[2] %}
                <td>{{ hop.delays[2] | round | int if hop.delays[0] else '*' }}ms</td>
                  {% else %}
                <td> * </td>
                  {% endif %}
    
                <td>{{ hop.hop_ip }}</td>
                <td>{{ hop.asn }}</td>
              </tr>
            {% endfor %}
          </tbody>
      </table>
      </div>
    </div>
        """,
        data_plane=state["data_plane"])


def render_delay_chart_fragment(state):
    return render_template_string(
        """
        <div id="delay-chart">
          <h2>Delay chart</h2>
          <img src="{{ url }}?ts={{ ts }}" alt="Delay chart">
        </div>
        """,
        url=state["delay_chart_url"], ts=state["ts"]
    )


def render_cplane_chart_fragment(state):
    return render_template_string(
        """
        <div id="cplane-chart">
          <h2>Control plane chart</h2>
          <img src="{{ url }}?ts={{ ts }}" alt="Control plane chart">
        </div>
        """,
        url=state["cplane_chart_url"], ts=state["ts"]
    )


def render_dplane_chart_fragment(state):
    return render_template_string(
        """
        <div id="dplane-chart">
          <h2>Data plane chart</h2>
          <img src="{{ url }}?ts={{ ts }}" alt="Data plane chart">
        </div>
        """,
        url=state["dplane_chart_url"], ts=state["ts"]
    )


def render_nav_fragment(state, traceroute_id):
    return render_template_string(
        """
        <div id="nav-ids">
          <a href="{{ url_for('dashboard', uuid=prev_id) }}">Previous</a> |
          <a href="{{ url_for('dashboard', uuid=next_id) }}">Next</a> |
          <span>Current: {{ curr }}</span>
        </div>
        """,
        prev_id=state["prev_id"], next_id=state["next_id"], curr=traceroute_id
    )


def compute_state(traceroute_id: str):
    """Fetch latest state and generate charts for a given traceroute id."""
    collection = db["traceroutes"]

    curr_data_plane = collection.find_one({"sensor_id": 2, "_id": ObjectId(f"{traceroute_id}")})
    if not curr_data_plane:
        return None

    destination_ip = curr_data_plane["destination_ip"]
    trace_hops = curr_data_plane["hops"]

    prev_data_plane = collection.find_one(
        {"destination_ip": destination_ip, "sensor_id": 2, "_id": {"$lt": ObjectId(traceroute_id)}},
        sort=[("_id", -1)]
    )
    next_data_plane = collection.find_one(
        {"destination_ip": destination_ip, "sensor_id": 2, "_id": {"$gt": ObjectId(traceroute_id)}},
        sort=[("_id", 1)]
    )

    # Delay chart
    print("update delay chart")
    delay_chart_fig = get_delay_chart(collection)
    delay_chart_url = save_fig_png(delay_chart_fig, prefix="delay_chart")

    # Control plane chart
    cplane_chart_fig, _ = get_cplane_chart(prefixes)
    cplane_chart_url = save_fig_png(cplane_chart_fig, prefix="cplane_chart")

    # # Data plane chart
    # dplane_chart_fig, dplane_hops_to_asn = get_dplane_chart(trace_hops, prefixes)
    # dplane_chart_url = save_fig_png(dplane_chart_fig, prefix="dplane_chart")

    #print(trace_hops)
    if trace_hops:
        dplane_chart_fig, dplane_hops_to_asn = get_dplane_chart(trace_hops, prefixes)

        if dplane_chart_fig:
            dplane_chart_url = save_fig_png(dplane_chart_fig, prefix="dplane_chart")

        else:
            dplane_chart_url = None

    if not trace_hops:
        dplane_chart_url = None

    # Annotate hops with ASN
    for hop in trace_hops:
        if hop["responded"]:
            hop_asn = dplane_hops_to_asn.get(hop["hop_ip"])
            hop["asn"] = hop_asn if hop_asn else "*"

        if not hop["responded"]:
            hop["asn"] = '*'

    return {
        "data_plane": curr_data_plane,
        "delay_chart_url": delay_chart_url,
        "cplane_chart_url": cplane_chart_url,
        "dplane_chart_url": dplane_chart_url,
        "prev_id": str(prev_data_plane["_id"]) if prev_data_plane else traceroute_id,
        "next_id": str(next_data_plane["_id"]) if next_data_plane else traceroute_id,
        # Timestamp used to bust browser cache on images
        "ts": int(time.time())
    }

def updater_loop():
    """Background updater that pushes Turbo replaces to the client every 3 minutes."""
    with app.app_context():
        while True:
            time.sleep(60)  # 3 minutes
            # We refresh based on the currently viewed UUID; if none, skip
            # For a single-page per UUID, you can derive it from request args during initial render.
            # Here we choose to refresh the last requested UUID if present; otherwise skip.
            # In multi-client setups, consider storing per-client UUID in session or pushing channels.
            traceroute_id = getattr(updater_loop, "last_uuid", None)
            if not traceroute_id:
                continue
            state = compute_state(traceroute_id)
            if not state:
                continue

            turbo.push(turbo.replace(render_data_plane_fragment(state), target="data-plane"))
            turbo.push(turbo.replace(render_delay_chart_fragment(state), target="delay-chart"))
            turbo.push(turbo.replace(render_cplane_chart_fragment(state), target="cplane-chart"))
            turbo.push(turbo.replace(render_dplane_chart_fragment(state), target="dplane-chart"))
            turbo.push(turbo.replace(render_nav_fragment(state, traceroute_id), target="nav-ids"))


# def background_thread():
#     print("get delay over time chart data")
#     collection = db["traceroutes"]
#
#     prev_timestamp = None
#     thread_sleep = 3
#
#     while True:
#         delay, timestamp = get_current_delay(collection)
#         print(delay, timestamp)
#
#         if not prev_timestamp or prev_timestamp < timestamp:
#             prev_timestamp = timestamp
#             socketio.emit('updateSensorData', {'value': round(int(delay)), "date": timestamp})
#
#         else:
#             print("wait for new delay")
#
#         socketio.sleep(thread_sleep)


def start_updater_thread():
    # Prevent double-start under Flask's debug reloader
    if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        t = threading.Thread(target=updater_loop, daemon=True)
        t.start()


def save_fig_png(fig, prefix="chart"):
    """Save a Matplotlib figure to a unique PNG under static/charts and return URL path."""
    # filename = f"{prefix}_{uuid.uuid4().hex}.png"
    filename = f"{prefix}.png"
    filepath = os.path.join(STATIC_DIR, filename)
    fig.tight_layout()
    #plt.savefig(filepath, format="png")
    plt.savefig(filepath, format="png", dpi=120)
    plt.close(fig)
    plt.clf()
    # Return a URL path the template can use
    return url_for("static", filename=f"charts/{filename}")


def get_latest_dplane_id(collection):
    # draw delay chart according to latest position
    mongo_project = {
        'sensor_id': 2,
        'destination_ip': '198.18.1.13'
    }
    mongo_filter = {'sensor_id': 2, 'destination_ip': '198.18.1.13'}
    mongo_sort = list({'timestamp': -1}.items())

    result = collection.find_one(
        filter=mongo_filter,
        projection=mongo_project,
        sort=mongo_sort)

    return result['_id']


@app.route("/", methods=['GET', 'POST'])
def dashboard():
    collection = db["traceroutes"]
    latest_result = get_latest_dplane_id(collection)

    print(latest_result)
    traceroute_id = request.args.get("uuid", default=ObjectId(f"{latest_result}"))
    state = compute_state(traceroute_id)
    if not state:
        return f"cannot find traceroute (uuid: {escape(traceroute_id)})"

    # Initial full page render
    return render_template(
        "dashboard.html",
        data_plane=state["data_plane"],
        delay_chart_url=state["delay_chart_url"],
        cplane_chart_url=state["cplane_chart_url"],
        dplane_chart_url=state["dplane_chart_url"],
        prev_id=state["prev_id"],
        next_id=state["next_id"],
        ts=state["ts"]
    )


# old
# @app.route("/")
# def dashboard():
#     collection = db["traceroutes"]
#
#     latest_dplane_id = get_latest_dplane_id(collection)
#     traceroute_id = request.args.get("uuid", default=ObjectId(f"{latest_dplane_id}"))
#
#     print(traceroute_id)
#
#     if not traceroute_id:
#         return f"cannot find traceroute (uuid: {traceroute_id})"
#
#     if traceroute_id:
#         curr_data_plane = collection.find_one({"sensor_id": 2, "_id": ObjectId(f"{traceroute_id}")})
#         print(f"destination_ip: {curr_data_plane}")
#         destination_ip = curr_data_plane['destination_ip']
#         trace_hops = curr_data_plane['hops']
#         print(f"destination_ip: {destination_ip}")
#
#         prev_data_plane = collection.find_one(
#             {"destination_ip": destination_ip, "sensor_id": 2, "_id": {"$lt": ObjectId(traceroute_id)}},
#             sort=[("_id", -1)])
#         next_data_plane = collection.find_one(
#             {"destination_ip": destination_ip, "sensor_id": 2, "_id": {"$gt": ObjectId(traceroute_id)}},
#             sort=[("_id", 1)])
#
#         # delay_chart_fig = get_delay_chart(collection)
#         # delay_chart_url = save_fig_png(delay_chart_fig, prefix="delay_chart")
#
#         # get control plane figure
#         cplane_chart_fig, _ = get_cplane_chart(prefixes)
#         cplane_chart_url = save_fig_png(cplane_chart_fig, prefix="cplane_chart")
#
#         print(trace_hops)
#         if trace_hops:
#             dplane_chart_fig, dplane_hops_to_asn = get_dplane_chart(trace_hops, prefixes)
#             dplane_chart_url = save_fig_png(dplane_chart_fig, prefix="dplane_chart")
#
#         if not trace_hops:
#             dplane_chart_url = None
#
#         for hop in trace_hops:
#             if not hop['responded']:
#                 continue
#
#             hop_asn = dplane_hops_to_asn[hop['hop_ip']]
#             if hop_asn:
#                 hop['asn'] = hop_asn
#             else:
#                 hop['asn'] = '*'
#
#         return render_template("dashboard.html",
#                                data_plane=curr_data_plane,
#                                cplane_chart_url=cplane_chart_url,
#                                dplane_chart_url=dplane_chart_url,
#                                prev_id=str(prev_data_plane["_id"]) if prev_data_plane else traceroute_id,
#                                next_id=str(next_data_plane["_id"]) if next_data_plane else traceroute_id)


@app.before_request
def remember_uuid():
    uuid_arg = request.args.get("uuid")
    if uuid_arg:
        updater_loop.last_uuid = uuid_arg


if __name__ == '__main__':
    # run monitor
    monitored_ip = "198.18.1.13"
    sensor_ip = "192.0.0.3"
    start = datetime.now() + timedelta(seconds=5)  # start 5 seconds from now
    end = start + timedelta(hours=3)  # run for 3 hours

    mongo_inserter = MongoInserter()
    mongo_inserter.connect()

    if not mongo_inserter.is_connect:
        exit(1)

    mongo_inserter.start()
    monitor = sensor.TraceMonitor(monitored_ip, sensor_ip, start, end)
    monitor.start()
    print("run server")
    start_updater_thread()
    app.run(host='192.0.0.3', debug=True, threaded=True)
