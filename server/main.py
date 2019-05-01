import sqlite3
from math import pi

import datetime
import json
import numpy as np
import os
import pandas as pd
import random
from bokeh.embed import json_item
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.transform import cumsum
from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def dashboard():
    return render_template('dashboard.html')


# TODO: Get basic details
# - Total time spent


# TODO: Make a different module called API which will contain all these endpoints
@app.route("/get_viz/timeline")
def get_timeline():
    df = _get_data()
    data_store = ColumnDataSource(data=df)
    tooltips = [("App", "@app_name")]

    p = figure(plot_width=1200, plot_height=200, tooltips=tooltips, tools='hover, zoom_in, zoom_out, reset, xpan',
               x_axis_type='datetime')
    p.yaxis.visible = False
    p.quad(left='starttime', right='endtime', top=10, bottom=0, source=data_store, color='color')
    return json.dumps(json_item(p, "timeline"))


# TODO: Show the actual time spent instead of the epoch and clean up this code
@app.route("/get_viz/per_app_usage")
def get_per_app_usage():
    df = _get_data()
    total_time_spent = df.duration.sum()
    per_app_df = df.groupby('app_name')['duration'].sum().sort_values(ascending=False).to_frame().reset_index()
    per_app_df['angle'] = np.nan
    per_app_df.angle = per_app_df.duration.apply(lambda x: x.seconds / total_time_spent.seconds * 2 * pi)
    per_app_df['color'] = np.nan
    color_map = _get_color_map(per_app_df, 'app_name')
    per_app_df['color'] = per_app_df.app_name.apply(lambda x: color_map[x])
    p = figure(plot_height=400, plot_width=400, toolbar_location=None,
               tools="hover", tooltips="@app_name: @duration")
    p.wedge(x=0, y=1, radius=0.9,
            start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
            line_color="white", fill_color='color', source=per_app_df)
    p.axis.axis_label = None
    p.axis.visible = False
    p.grid.grid_line_color = None
    return json.dumps(json_item(p, "per_app_usage"))


# TODO: Figure out a way to persist this
def _get_data():
    conn = sqlite3.connect(os.path.expanduser('~/basil.db'))
    cur = conn.cursor()
    data = cur.execute("select * from application_snapshots;").fetchall()
    df = pd.DataFrame(data)
    df = df.rename(columns={
        0: 'title',
        1: 'app_name',
        2: 'starttime',
        3: 'duration'
    })
    df['endtime'] = np.nan
    df['color'] = np.nan
    df.starttime = df.starttime.apply(lambda x: datetime.datetime.fromtimestamp(x))
    df.duration = df.duration.apply(lambda x: datetime.timedelta(seconds=x))
    df['endtime'] = df.starttime + df.duration
    color_map = _get_color_map(df, 'app_name')
    df.color = df.app_name.apply(lambda x: color_map[x])
    return df


def _get_color_map(df, col_name):
    color_map = {}
    r = lambda: random.randint(0, 255)
    for color in df[col_name].unique():
        color_map[color] = '#%02X%02X%02X' % (r(), r(), r())
    return color_map
