import numpy as np
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import streamlit_nested_layout
from pygame import mixer

from datetime import datetime
import glob
import os

import conf

import common_model
from common_model import read_data
from owlet_model import clean_data
from chart_util import build_dual_axis_altair_time_chart

mixer.init() 

### Init

st.set_page_config(layout="wide")

### Sidebar

scrape_time = st.sidebar.number_input("Scrape time (sec)", min_value=5, max_value=60, value=5, step=1)

metric_c1, metric_c2 = st.sidebar.columns(2)

with metric_c1:
  metric_time = st.number_input("Avg time", min_value=0, value=1, step=1)
with metric_c2:
  metric_unit = st.selectbox("Avg unit", ("sec", "min"), index=1) 

metric_mult = 60 if metric_unit == "min" else 1
data_points_count = int(round((metric_time * metric_mult) / scrape_time))

st.sidebar.markdown("""---""")

alarm_active = st.sidebar.checkbox("Alarm active?", value = False)

base_resource_path = "./resources/audio/"
alarm_options = list(map(os.path.basename, glob.glob(f"{base_resource_path}*.mp3")))
alarm_sound_option = st.sidebar.selectbox("Alarm sound?", alarm_options, index=0) 
mixer.music.load(f"{base_resource_path}{alarm_sound_option}")

alarm_threshold_o2 = st.sidebar.number_input("Alarm threshold (avg O2)", min_value=80, max_value=98, value=90, step=1)
alarm_threshold_bpm = st.sidebar.number_input("Alarm threshold (avg BPM)", min_value=60, max_value=90, value=80, step=1)
  
alarm_threshold_perc_missing = st.sidebar.number_input("Missing points threshold %", min_value=0, max_value=100, value=50, step=10)
alarm_threshold_count_missing = int(round(data_points_count * (alarm_threshold_perc_missing / 100)))

st.sidebar.text(f"Miss threshold: {alarm_threshold_count_missing}")

### Auto-refresh

st_autorefresh(interval=scrape_time * 1000, key="loop")

### State init

@st.cache
def get_ocr_model():
  return common_model.get_ocr_model()

if "df" not in st.session_state:
  print("Starting empty data..")
  st.session_state.df = pd.DataFrame()

if "df_metric" not in st.session_state:
  print("Starting empty data metrics..")
  st.session_state.df_metric = pd.DataFrame()

if "conf" not in st.session_state:
  print("Reading conf..")
  st.session_state.conf = conf.read_conf()

if "ocr" not in st.session_state:
  print("Setting model..")
  st.session_state.ocr = get_ocr_model()

### State run

new_data = pd.DataFrame([clean_data(read_data(st.session_state.conf, st.session_state.ocr))])
st.session_state.df = pd.concat([st.session_state.df, new_data], ignore_index=True)

recent_points = st.session_state.df.tail(data_points_count).sort_values(by="time", ascending=False)
status_is_None = recent_points["status"].isna()
not_charging = ~recent_points["status"].str.contains("charging", na=False, case=False)
valid_recent_points = recent_points[status_is_None | not_charging]

bpm_valid_points = valid_recent_points["bpm"].count()
o2_valid_points = valid_recent_points["o2"].count()

bpm_metric = round(valid_recent_points["bpm"].sum(axis=0, skipna=True) / bpm_valid_points, 2) if bpm_valid_points > 0 else None
o2_metric = round(valid_recent_points["o2"].sum(axis=0, skipna=True) / o2_valid_points, 2) if o2_valid_points > 0 else None

bpm_missing = valid_recent_points["bpm"].isna().sum()
o2_missing =  valid_recent_points["o2"].isna().sum()

new_metric_data = pd.DataFrame([
  { 
    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "bpm": bpm_metric,
    "o2": o2_metric
  }
])
st.session_state.df_metric = pd.concat([st.session_state.df_metric, new_metric_data], ignore_index=True)

### Alarm run

if (
  alarm_active and (
    (o2_metric is not None and o2_metric < alarm_threshold_o2) or 
    (bpm_metric is not None and bpm_metric < alarm_threshold_bpm) or
    (bpm_missing > alarm_threshold_count_missing) or
    (o2_missing > alarm_threshold_count_missing)
  )
):
  mixer.music.play()
else:
  mixer.music.stop()

### Dashboard

raw_chart = build_dual_axis_altair_time_chart(
  data = st.session_state.df, title = "Sensor readings", time_interval = scrape_time, time_unit = "sec", 
  time_field = "time",
  field1 = "o2", field1_tooltip = "Oxigen %", field1_domain = [80, 100], field1_color = "#1E90FF",
  field2 = "bpm", field2_tooltip = "BPM", field2_domain = [70, 150], field2_color = "#DC143C"
)
metric_chart = build_dual_axis_altair_time_chart(
  data = st.session_state.df_metric, title = "Average metrics", time_interval = metric_time, time_unit = metric_unit, 
  time_field = "time",
  field1 = "o2", field1_tooltip = "Oxigen %", field1_domain = [80, 100], field1_color = "#1E90FF",
  field2 = "bpm", field2_tooltip = "BPM", field2_domain = [70, 150], field2_color = "#DC143C"
)

viz, data = st.columns([2, 1])

with viz:
  m1, m2, m3, m4 = st.columns([1, 1, 1, 1])

  with m1:
    st.metric(f"avg O2 ({metric_time} {metric_unit})", o2_metric)

  with m2:
    st.metric(f"avg BPM ({metric_time} {metric_unit})", bpm_metric)

  with m3:
    st.metric(f"miss O2 ({metric_time} {metric_unit})", o2_missing)

  with m4:
    st.metric(f"miss BPM ({metric_time} {metric_unit})", bpm_missing)

  st.altair_chart(raw_chart, use_container_width=True)
  st.altair_chart(metric_chart, use_container_width=True)

with data:
  st.dataframe(recent_points, height = 800)