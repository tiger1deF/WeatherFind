import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time, sys, os
import pandas as pd
from datetime import datetime
from meteostat import Point, Daily
from geopy.geocoders import Nominatim

st.title('Weather Data Downloader')

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
if st.sidebar.checkbox('Plot metrics', True):
    plot = True
else:
    plot = False
start = st.sidebar.slider("Start Year", min_value=1966, 
                          max_value=2023, value=2000, 
                          step=1)
end = st.sidebar.slider("End Year", min_value=start, 
                          max_value=2023, value=2023, 
                          step=1)

st.write('Accepts ZIP code, location name, or coordinates')
location = str(st.sidebar.text_input('Location', "Boston"))

@st.cache_resource
def predict_weather(location = location, start = start, 
                        metrics = metrics, plot = plot,
                        end = end):
    normal_loc = location
    # Obtains latitude and longitude of location
    geolocator = Nominatim(user_agent = "weather_predict")
    location = geolocator.geocode(location)
    coords = (location.latitude, location.longitude)
    maploc = pd.DataFrame([coords[0], coords[1]], columns = ['lat', 'lon'])
    st.map(maploc)
    # Obtains time range 
    if start == 2023:
        end = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
    else:
        end = datetime(end, 1, 1)
    start_year = start
    start = datetime(start, 1, 1)

    # Obtains past weather info 
    location = Point(coords[0], coords[1])
    weather = Daily(location, start, end).fetch()
    dates = [str(i) for i in weather.index.values]
    weather.index = [i for i in range(0, len(weather))]
    if metrics == 'all':
        feature = pd.concat((weather, pd.DataFrame({'date':dates})), axis = 1)
    else:
        feature = pd.concat((weather[metrics], pd.DataFrame({'date':dates})), axis = 1)

    if plot == True and metrics != 'all':
        fig, axs = plt.subplots(1, len(metrics))
        xx = [start_year + i/365.25 for i in range(0, len(weather))]
        for count in range(0, len(metrics)):
            axs[count].set_title(f'{encoder[metrics[count]]} from {start} to {end}')
            axs[count].set_xlabel('Time (years)')
            axs[count].set_ylabel(stats[[metrics[count]]])
            axs[count].plot(xx, list(feature[metrics[count]]))
        plt.show()
    text = feature.to_csv()
    download = st.sidebar.text_input('Download Location', '$HOME/Downloads')
    st.download_button('Download Metrics', text, f'{normal_loc}-weather.csv') 
    os.system(f'mv Results.csv {download}')

if st.button("Obtain Metrics"):
    with st.spinner('Fetching Data...'):
        predict_weather()
