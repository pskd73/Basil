import datetime
import json
import os
import random
import sqlite3
from math import pi

import numpy as np
import pandas as pd
from bokeh.embed import json_item
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.transform import cumsum
from flask import Flask, render_template

app = Flask(__name__)


# TODO: Add support for projects
# TODO: Add support for adding programs into categories. For example: Firefox => Browsing
# TODO: Figure out a way to make the colors consistent and allow a list of colors only
def _get_color_map(inp_df, col_name):
    inp_df_color_map = {}
    r = lambda: random.randint(0, 255)
    for color in inp_df[col_name].unique():
        inp_df_color_map[color] = '#%02X%02X%02X' % (r(), r(), r())
    return inp_df_color_map


def _get_data():
    conn = sqlite3.connect(os.path.expanduser('~/basil.db'))
    cur = conn.cursor()
    data = cur.execute("select * from application_snapshots;").fetchall()
    db_df = pd.DataFrame(data)
    db_df = db_df.rename(columns={
        0: 'title',
        1: 'app_name',
        2: 'start_time',
        3: 'duration'
    })
    db_df['end_time'] = np.nan
    db_df['color'] = np.nan
    db_df.start_time = db_df.start_time.apply(lambda x: datetime.datetime.fromtimestamp(x))
    db_df.duration = db_df.duration.apply(lambda x: datetime.timedelta(seconds=x))
    db_df['end_time'] = db_df.start_time + db_df.duration
    db_df_color_map = _get_color_map(db_df, 'app_name')
    db_df.color = db_df.app_name.apply(lambda x: db_df_color_map[x])
    return db_df, db_df_color_map


df, color_map = _get_data()


@app.route('/')
def dashboard():
    basic_info = get_basic_info()
    return render_template('dashboard.html', basic_info=basic_info)


# TODO: Make a different module called API which will contain all these endpoints
def get_basic_info():
    return {
        'active_min': df['duration'].sum().seconds // 60,
    }


@app.route("/get_viz/timeline")
def get_timeline():
    data_store = ColumnDataSource(data=df)
    tooltips = [("App", "@app_name")]

    p = figure(plot_width=1200, plot_height=200, tooltips=tooltips, tools='hover, zoom_in, zoom_out, reset, xpan',
               x_axis_type='datetime', sizing_mode='scale_both')
    p.yaxis.visible = False
    p.quad(left='start_time', right='end_time', top=10, bottom=0, source=data_store, color='color')
    return json.dumps(json_item(p, "timeline"))


@app.route("/get_viz/per_app_usage")
def get_per_app_usage():
    total_time_spent = df.duration.sum()
    per_app_df = df.groupby('app_name')['duration'].sum().sort_values(ascending=False).to_frame().reset_index()
    per_app_df['angle'] = np.nan
    per_app_df['color'] = np.nan
    per_app_df.angle = per_app_df.duration.apply(lambda x: x.seconds / total_time_spent.seconds * 2 * pi)
    per_app_df['color'] = per_app_df.app_name.apply(lambda x: color_map[x])
    per_app_df['duration_min'] = per_app_df['duration'].apply(lambda x: x.seconds // 60)
    p = figure(plot_height=400, plot_width=400, toolbar_location=None,
               tools="hover", tooltips="@app_name: @duration_min min")
    p.wedge(x=0, y=1, radius=0.9,
            start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
            line_color="white", fill_color='color', source=per_app_df)
    p.axis.axis_label = None
    p.axis.visible = False
    p.grid.grid_line_color = None
    return json.dumps(json_item(p, "per_app_usage"))
