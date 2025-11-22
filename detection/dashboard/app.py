from detection.system.analysis.get_delay_chart import get_delay_chart
from detection.system.analysis.get_cplane_chart import get_cplane_chart
from detection.system.analysis.get_dplane_chart import get_dplane_chart
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask import request, Flask, render_template, url_for
from markupsafe import escape
import os
import pandas as pd
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

# mongodb config
client = MongoClient("mongodb://localhost:27017/")
db = client["network_monitoring"]

# flask config
app = Flask(__name__)
STATIC_DIR = os.path.join(app.root_path, "static", "charts")
os.makedirs(STATIC_DIR, exist_ok=True)

# other configs
prefix2as_csv = r"D:\Documents\open university\netSeminar\source\detection\detection_tools\prefix2as.csv"
prefixes = pd.read_csv(prefix2as_csv)


def save_fig_png(fig, prefix="chart"):
    """Save a Matplotlib figure to a unique PNG under static/charts and return URL path."""
    # filename = f"{prefix}_{uuid.uuid4().hex}.png"
    filename = f"{prefix}.png"
    filepath = os.path.join(STATIC_DIR, filename)
    fig.tight_layout()
    plt.savefig(filepath, format="png", dpi=120)
    plt.close(fig)
    plt.clf()
    # Return a URL path the template can use
    return url_for("static", filename=f"charts/{filename}")


@app.route("/", methods=['GET', 'POST'])
def dashboard():
    collection = db["traceroutes"]

    traceroute_id = request.args.get("uuid", default="6921970e5742bca490a77f4a")

    print(traceroute_id)

    if not traceroute_id:
        return f"cannot find traceroute (uuid: {traceroute_id})"

    if traceroute_id:
        curr_data_plane = collection.find_one({"sensor_id": 2, "_id": ObjectId(f"{traceroute_id}")})
        destination_ip = curr_data_plane['destination_ip']
        trace_hops = curr_data_plane['hops']
        print(f"destination_ip: {destination_ip}")

        prev_data_plane = collection.find_one(
            {"destination_ip": destination_ip, "sensor_id": 2, "_id": {"$lt": ObjectId(traceroute_id)}},
            sort=[("_id", -1)])
        next_data_plane = collection.find_one(
            {"destination_ip": destination_ip, "sensor_id": 2, "_id": {"$gt": ObjectId(traceroute_id)}},
            sort=[("_id", 1)])

        # print(curr_data_plane)
        delay_chart_fig = get_delay_chart(collection)
        delay_chart_url = save_fig_png(delay_chart_fig, prefix="delay_chart")

        # get control plane figure
        cplane_chart_fig, _ = get_cplane_chart(prefixes)
        cplane_chart_url = save_fig_png(cplane_chart_fig, prefix="cplane_chart")

        dplane_chart_fig, dplane_hops_to_asn = get_dplane_chart(trace_hops, prefixes)
        dplane_chart_url = save_fig_png(dplane_chart_fig, prefix="dplane_chart")

        for hop in trace_hops:
            hop_asn = dplane_hops_to_asn[hop['hop_ip']]
            if hop_asn:
                hop['asn'] = hop_asn
            else:
                hop['asn'] = '*'

        return render_template("dashboard.html",
                               data_plane=curr_data_plane,
                               delay_chart_url=delay_chart_url,
                               cplane_chart_url=cplane_chart_url,
                               dplane_chart_url=dplane_chart_url,
                               prev_id=str(prev_data_plane["_id"]) if prev_data_plane else traceroute_id,
                               next_id=str(next_data_plane["_id"]) if next_data_plane else traceroute_id)


if __name__ == '__main__':
    app.run(host='192.0.0.3', debug=True)