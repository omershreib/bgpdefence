from config import CONFIG
from detection.dashboard.dashboard_tools import compute_state, updater_loop
from detection.system.database.get_latest_data_plane_id import get_latest_data_plane_id
from detection.system.sensor import trace_monitor
from external.bgp_table_to_ftp import bgp_worker
from detection.system.database.mongo_inserter import MongoInserter, make_mongo_inserter_parameters
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask import request, Flask, render_template, Response
from turbo_flask import Turbo
from threading import Lock
from markupsafe import escape
from bson.json_util import dumps
import threading
import os
import pandas as pd

# background thread
thread = None
thread_lock = Lock()

# mongodb config
client = MongoClient("mongodb://localhost:27017/")
db = client["network_monitoring"]

# flask config
app = Flask(__name__)
app.config['SERVER_NAME'] = 'BGPDashbard'
app.config['SECRET_KEY'] = 'bgphijack'
turbo = Turbo(app)

STATIC_DIR = os.path.join(app.root_path, "static", "charts")
CONFIG['static_dir'] = STATIC_DIR
os.makedirs(STATIC_DIR, exist_ok=True)

# prefix2as configs
prefixes = pd.read_csv(CONFIG['utilites']['prefix2as'])


def start_updater_thread():
    # prevent double-start under Flask's debug reloader
    if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        t = threading.Thread(target=updater_loop.updater_loop, args=(app, turbo), daemon=True)
        t.start()


@app.route("/live_dashboard_data")
def live_dashboard_data():
    collection = db["traceroutes"]
    latest_result = get_latest_data_plane_id(collection)

    uuid_arg = request.args.get("uuid")
    traceroute_id = uuid_arg or str(latest_result)

    state = compute_state.compute_state(collection, prefixes, traceroute_id)
    if not state:
        return Response(dumps({"error": f"cannot find traceroute (uuid: {traceroute_id})"}),
                        mimetype="application/json")

    payload = {
        "data_plane": state["data_plane"],
        "delay_chart_url": state["delay_chart_url"],
        "control_plane_chart_url": state["control_plane_chart_url"],
        "data_plane_chart_url": state["data_plane_chart_url"],
        "prev_id": state.get("prev_id"),
        "next_id": state.get("next_id"),
        "ts": state["ts"],
    }
    return Response(dumps(payload), mimetype="application/json")


@app.route("/live_dashboard")
def live_dashboard():
    collection = db["traceroutes"]
    latest_result = get_latest_data_plane_id(collection)

    print(latest_result)
    traceroute_id = request.args.get("uuid", default=ObjectId(f"{latest_result}"))
    state = compute_state.compute_state(collection, prefixes, traceroute_id)
    if not state:
        return f"cannot find traceroute (uuid: {escape(traceroute_id)})"

    # Initial full page render
    return render_template(
        "base_live.html",
        data_plane=state["data_plane"],
        delay_chart_url=state["delay_chart_url"],
        control_plane_chart_url=state["control_plane_chart_url"],
        data_plane_chart_url=state["data_plane_chart_url"],
        prev_id=state["prev_id"],
        next_id=state["next_id"],
        ts=state["ts"]
    )


@app.route("/", methods=['GET', 'POST'])
def dashboard():
    collection = db["traceroutes"]
    latest_result = get_latest_data_plane_id(collection)

    print(latest_result)
    traceroute_id = request.args.get("uuid", default=ObjectId(f"{latest_result}"))
    state = compute_state.compute_state(collection, prefixes, traceroute_id)
    if not state:
        return f"cannot find traceroute (uuid: {escape(traceroute_id)})"

    # Initial full page render
    return render_template(
        "base.html",
        data_plane=state["data_plane"],
        delay_chart_url=state["delay_chart_url"],
        control_plane_chart_url=state["control_plane_chart_url"],
        data_plane_chart_url=state["data_plane_chart_url"],
        prev_id=state["prev_id"],
        next_id=state["next_id"],
        ts=state["ts"]
    )


@app.before_request
def remember_uuid():
    uuid_arg = request.args.get("uuid")
    if uuid_arg:
        updater_loop.last_uuid = uuid_arg


def run_app(monitor_parameters):

    # start mongo inserter thread
    mongo_inserter = MongoInserter(**make_mongo_inserter_parameters(CONFIG['system']['mongoDB']))
    mongo_inserter.start()

    # start traceroute monitor thread
    monitor = trace_monitor.TraceMonitor(**monitor_parameters)
    monitor.start()

    # start FTP uploader worker thread
    ftp_uploader = threading.Thread(target=bgp_worker, daemon=True)
    ftp_uploader.start()

    # run dashboard application
    start_updater_thread()
    app.run(host='192.0.0.3', port=5000, debug=True, threaded=True)
