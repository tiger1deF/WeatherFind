import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time, sys, os
import pandas as pd
from datetime import datetime
from meteostat import Point, Daily
from geopy.geocoders import Nominatim
import torch

st.title('LSTM RNN Weather Predictor')
encoder = {'tavg':'Average Temperature', 'tmin': 'Minimum Temperature',
        'tmax': 'Maximum Temperature', 'wspd': 'Wind Speed',
        'prcp': 'Precipitation', 'pres':'Pressure'}
stats = {'tavg': 'Temperature (C)', 'tmin': 'Temperature (C)',
        'tmax': 'Temperature (C)', 'wspd': 'Wind Speed (km/h)',
        'prcp': 'Precipitation (mm)', 'pres': 'Millibars (mb)'}
(c1, c2, c3, c7) = st.columns(4)
(c4, c5, c6) = st.columns(3)
metrics = []
with c1:
    if st.checkbox('Average Temperature', False):
        metrics.append("tavg")
with c2:
    if st.checkbox('Minimum Temperature', False):
        metrics.append("tmin")
with c3:
    if st.checkbox('Maximum Temperature', False):
        metrics.append("tmax")
with c4:
    if st.checkbox('Precipitation Amount', False):
        metrics.append("prcp")
with c5:
    if st.checkbox('Wind Speed', False):
        metrics.append("wspd")
with c6:
    if st.checkbox('Pressure', False):
        metrics.append("pres")
with c7:
    if st.checkbox('All', True):
        metrics = 'all'