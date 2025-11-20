from detection.system.analysis.get_data_plane_delay import get_data_plane_delay
from get_delay_chart import get_delay_chart
from detection.system.analysis.get_cplane_chart import get_cplane_chart
from pymongo import MongoClient, errors
from bson.objectid import ObjectId
from flask import request, Flask, render_template, stream_template, url_for
from markupsafe import escape
import io
import base64
import os
import uuid
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
#plt.style.use('fivethirtyeight')
#plt.style.use('dark_background')
#plt.style.use('grayscale')

def save_fig_png(fig, prefix="chart"):
    """Save a Matplotlib figure to a unique PNG under static/charts and return URL path."""
    #filename = f"{prefix}_{uuid.uuid4().hex}.png"
    filename = f"{prefix}.png"
    filepath = os.path.join(STATIC_DIR, filename)
    fig.tight_layout()
    plt.savefig(filepath, format="png", dpi=120)
    plt.close(fig)
    plt.clf()
    # Return a URL path the template can use
    return url_for("static", filename=f"charts/{filename}")


@app.route("/hello")
def hello():
    name = request.args.get("name", "Flask")
    return f"Hello, {escape(name)}!"


@app.route("/dashboard/traceroute", methods=['GET', 'POST'])
def show_traceroute():
    collection = db["traceroutes"]

    traceroute_id = request.args.get("uuid", default=0)

    print(traceroute_id)

    if not traceroute_id:
        return f"cannot find traceroute (uuid: {traceroute_id})"

    # 691dc51910d50060d21782a4
    if traceroute_id:
        curr_data_plane = collection.find_one({"_id": ObjectId(f"{traceroute_id}")})

    prev_data_plane = collection.find_one({"_id": {"$lt": ObjectId(traceroute_id)}}, sort=[("_id", -1)])
    next_data_plane = collection.find_one({"_id": {"$gt": ObjectId(traceroute_id)}}, sort=[("_id", 1)])


    for hop in curr_data_plane['hops']:
        hop['asn'] = 5

    print(curr_data_plane)
    delay_chart_fig= get_delay_chart(collection)
    delay_chart_url = save_fig_png(delay_chart_fig, prefix="delay_chart")

    cplane_chart_fig = get_cplane_chart()
    cplane_chart_url = save_fig_png(cplane_chart_fig, prefix="cplane_chart")

    return render_template("dashboard.html",
                           data_plane=curr_data_plane,
                           delay_chart_url=delay_chart_url,
                           cplane_chart_url=cplane_chart_url,
                           prev_id=str(prev_data_plane["_id"]) if prev_data_plane else traceroute_id,
                           next_id=str(next_data_plane["_id"]) if next_data_plane else traceroute_id)


if __name__ == '__main__':
    # run client web dashboard
    app.run(host='localhost', debug=True)
