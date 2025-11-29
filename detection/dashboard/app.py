from config import CONFIG
from detection.utilities.prefix2as import prefix2as
from detection.dashboard.tools.compute_state import compute_state
from detection.system.database.get_latest_data_plane_id import get_latest_data_plane_id
from detection.system.sensor import trace_monitor
from external.bgp_table_to_ftp import bgp_worker
from detection.system.database.mongo_inserter import MongoInserter, make_mongo_inserter_parameters
from pymongo import MongoClient
from flask import request, Flask, render_template, redirect, url_for
from markupsafe import escape
import threading
import os

# mongodb config
MONGO_CLIENT_URL = CONFIG['system']['mongoDB']['client_url']
MONGO_DATABASE = CONFIG['system']['mongoDB']['prod_database']
MONGO_COLLECTION = CONFIG['system']['mongoDB']['collection']

# mongoDB connection setup
client = MongoClient(MONGO_CLIENT_URL)
db = client[MONGO_DATABASE]
collection = db[MONGO_COLLECTION]

# flask config
app = Flask(__name__)
app.config['SERVER_NAME'] = CONFIG['system']['flask_app']['server_name']
app.config['SECRET_KEY'] = CONFIG['system']['flask_app']['secret_key']
app.config['DEBUG'] = True

SERVER_HOST = CONFIG['system']['flask_app']['host']
SERVER_PORT = CONFIG['system']['flask_app']['port']

STATIC_DIR = os.path.join(app.root_path, "static", "charts")
CONFIG['static_dir'] = STATIC_DIR
os.makedirs(STATIC_DIR, exist_ok=True)

# prefix2as configs
# note: this prefix2as file contains data about all the address prefixes used in the GNS3 lab simulation
#       and needed because not all the prefixes are announced in the lab (meaning that it is not possible to
#       learn about all the prefixes in the project from the localISP routing table alone)
prefixes = prefix2as.load_prefixes(CONFIG['utilities']['prefix2as'])


@app.route("/")
def root():
    return redirect(url_for('dashboard'))


@app.route("/live_dashboard")
def live_dashboard():
    traceroute_id = str(get_latest_data_plane_id(collection))
    state = compute_state(collection, prefixes, traceroute_id)
    update_charts = not request.args.get('only_stream_raw_data_plane')

    if not state:
        return f"cannot find traceroute (uuid: {escape(traceroute_id)})"

    data_context = {
        "data_plane": state["data_plane"],
        "delay_chart_url": state["delay_chart_url"],
        "control_plane_chart_url": state["control_plane_chart_url"],
        "data_plane_chart_url": state["data_plane_chart_url"],
        "prev_id": state.get("prev_id"),
        "next_id": state.get("next_id"),
        "ts": state["ts"],
        "update_charts": update_charts
    }

    if request.args.get("only_stream_raw_data_plane"):
        data_context.pop("ts")

    return render_template("base_live.html", **data_context)


@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    latest_result = get_latest_data_plane_id(collection)
    update_charts = not request.args.get('only_stream_raw_data_plane')
    traceroute_id = request.args.get("uuid")

    if not traceroute_id:
        traceroute_id = latest_result

    state = compute_state(collection, prefixes, traceroute_id)
    if not state:
        return f"cannot find traceroute (uuid: {escape(traceroute_id)})"

    data_context = {
        "data_plane": state["data_plane"],
        "delay_chart_url": state["delay_chart_url"],
        "control_plane_chart_url": state["control_plane_chart_url"],
        "data_plane_chart_url": state["data_plane_chart_url"],
        "prev_id": state.get("prev_id"),
        "next_id": state.get("next_id"),
        "ts": state["ts"],
        "update_charts": update_charts
    }

    if request.args.get("only_stream_raw_data_plane"):
        data_context.pop("ts")

    return render_template("base.html", **data_context)


def run_app():
    """RunApp (project's runner)

    this function runs all the project's threads:

        TraceMonitor: perform periodic traceroute tasks and push their results to a queue.

        MongoInserter:  periodically pull out new traceroute results from the queue and insert
                        them to a mongoDB database.

        bgp_worker: upload BGP snapshot of the localISP router to an FTP server (required in the GNS3 lab
                    because EEM script that should do exactly this procedure on a real Cisco equipment does not
                    supported in this lab)

    after all these threads run in background, the flask application framework in than started.
    """

    # load parameters for MongoInserter and TraceMonitor
    mongo_parameters = make_mongo_inserter_parameters(CONFIG['system']['mongoDB'])
    monitor_parameters = CONFIG['system']['monitor_setup']

    # start mongo inserter thread
    mongo_inserter = MongoInserter(**mongo_parameters)
    mongo_inserter.start()

    # start traceroute monitor thread
    monitor = trace_monitor.TraceMonitor(**monitor_parameters)
    monitor.start()

    # start FTP uploader worker thread (should enable only on GNS3 lab environment)
    ftp_uploader = threading.Thread(target=bgp_worker, daemon=True)
    ftp_uploader.start()

    # run dashboard application
    app.run(host=SERVER_HOST, port=SERVER_PORT, threaded=True)
