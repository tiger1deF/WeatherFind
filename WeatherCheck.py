import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time, sys, os
import pandas as pd
from datetime import datetime
from meteostat import Point, Daily
from geopy.geocoders import Nominatim

(c1, c2, c3) = st.columns(3)
with c2:
    st.title('WeatherCheck')

# Encoders to convert geopy metrics into plaintext weather metrics
encoder = {'tavg':'Average Temperature', 'tmin': 'Minimum Temperature',
        'tmax': 'Maximum Temperature', 'wspd': 'Wind Speed',
        'prcp': 'Precipitation', 'pres':'Pressure'}
stats = {'tavg': 'Temperature', 'tmin': 'Temperature',
        'tmax': 'Temperature', 'wspd': 'Wind Speed (km/h)',
        'prcp': 'Precipitation (mm)', 'pres': 'Millibars (mb)'}

# Identifies if temperatures will be reported in C or F
temp = st.sidebar.radio(
    'Temperature Unit',
    ("Fahrenheight", "Celsius"))

# Identifies what metrics will be plotted
metrics = []
(c1, c2, c3, c7) = st.columns(4)
(c4, c5, c6) = st.columns(3)
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

# Choose the range of dates to pull metrics from
start = st.sidebar.slider("Start Year", min_value=1900, max_value=2023, value=2000, step=1)
end = st.sidebar.slider("End Year", min_value=start, max_value=2023, value=2023, step=1)

# Choose initial location
st.write('Accepts ZIP code, location name, or coordinates')
location = str(st.sidebar.text_input('Location', "Boston"))
regular_loc = location

# Function for pulling, plotting, and comparing metrics
def predict_weather(location = location, start = start, metrics = metrics, plot = plot,
                    end = end, compare = False, compmetrics = ()):

    if compare == False:
        normal_loc = location
    else:
        compare_loc = location

    # Obtains latitude and longitude of location
    geolocator = Nominatim(user_agent = "weather_predict")
    location = geolocator.geocode(location)
    coords = (location.latitude, location.longitude)
    maploc = pd.DataFrame({'lat':coords[0], 'lon':coords[1]}, index = [0])
    if compare == False:
        with st.expander("Mapped Location"):
            st.map(maploc)
    else:
        with st.expander("Mapped Comparison Location"):
            st.map(maploc)

    # Obtains time range 
    if end == 2023:
        end = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
    else:
        end = datetime(end, 1, 1)
    start = datetime(start, 1, 1)

    # Obtains past weather info 
    location = Point(coords[0], coords[1])
    weather = Daily(location, start, end).fetch()

    # Performs Fahrenheight/Celsius conversions
    temperatures = ['tavg', 'tmin', 'tmax']
    if temp == 'Fahrenheight':
        for t in temperatures:
            weather[t] = [32 + (9/5) * i for i in weather[t]]
            stats[t] = stats[t] + ' (F)'
    else:
        for t in temperatures:
            stats[t] = stats[t] + ' (C)'

    dates = [str(i) for i in weather.index.values]
    weather.index = [i for i in range(0, len(weather))]
    start_year = int(str(dates[0]).split('-')[0])
    if metrics == 'all':
        feature = pd.concat((weather, pd.DataFrame({'date':dates})), axis = 1)
    else:
        if compare == False:
            feature = pd.concat((weather[metrics], pd.DataFrame({'date':dates})), axis = 1)
        else:
            compare_feature = pd.concat((weather[metrics], pd.DataFrame({'date':dates})), axis = 1)

    # Plots data if applicable
    xx = [start_year + i/365.25 for i in range(0, len(weather))]
    if compare == False:
        if plot == True and metrics != 'all':
            plt.tight_layout()
            fig, axs = plt.subplots(1, len(metrics))
            
            try:
                fig.set_figwidth(8 + 2.5 * len(metrics))
                for count in range(0, len(metrics)):
                    axs[count].set_title(f'{encoder[metrics[count]]} in {normal_loc}' + '\n' + f'from {str(start).split(" ")[0]} to {str(end).split(" ")[0]}')
                    axs[count].set_xlabel('Time (years)')
                    axs[count].set_ylabel(stats[metrics[count]])
                    axs[count].plot(xx, list(feature[metrics[count]]), linewidth = .5)
            except:
                axs.set_title(f'{encoder[metrics[0]]} in {normal_loc}' + '\n' + f'from {str(start).split(" ")[0]} to {str(end).split(" ")[0]}')
                axs.set_xlabel('Time (years)')
                axs.set_ylabel(stats[metrics[0]])
                axs.plot(xx, list(feature[metrics[0]]), linewidth = .5)
            
            with st.expander('Data Charts'):
                st.pyplot(fig)
    else:
        plt.tight_layout()
        fig, axs = plt.subplots(1, len(metrics))
        try:
            fig.set_figwidth(8 + 2.5 * len(metrics))
            for count in range(0, len(metrics)):
                axs[count].set_title(f'{encoder[metrics[count]]} for {regular_loc} vs {compare_loc}' + '\n' + f'from {str(start).split(" ")[0]} to {str(end).split(" ")[0]}')
                axs[count].set_xlabel('Time (years)')
                axs[count].set_ylabel(stats[metrics[count]])
                axs[count].plot(xx, list(compmetrics[metrics[count]]), linewidth = .5, label = regular_loc)
                axs[count].plot(xx, list(compare_feature[metrics[count]]), linewidth = .5, label = compare_loc)
                axs[count].legend()
        except:
            axs.set_title(f'{encoder[metrics[0]]} for {regular_loc} vs {compare_loc}' + '\n' + f'from {str(start).split(" ")[0]} to {str(end).split(" ")[0]}')
            axs.set_xlabel('Time (years)')
            axs.set_ylabel(stats[metrics[0]])
            axs.plot(xx, list(compmetrics[metrics[0]]), linewidth = .5, label = regular_loc)
            axs.plot(xx, list(compare_feature[metrics[0]]), linewidth = .5, label = compare_loc)
            axs.legend()

        with st.expander('Comparison Charts'):
            st.pyplot(fig)

    try:
        text = feature.to_csv()
    except:
        text = compmetrics.to_csv()

    try:
        st.download_button('Download Metrics', text, f'{normal_loc}-weather.csv')
    except:
         st.download_button('Download Comparison Location Metrics', text, f'{compare_loc}-weather.csv')
    if compare != True:
        return feature

compare_location = st.sidebar.text_input('Pick Comparison Location', 'Houston')\

download = st.sidebar.text_input('Main Download Location', '$HOME/Downloads')

(c1, c2, c3) = st.columns(3)
with c1:
    button = st.button("Obtain Location Metrics")
if button == True:
    with st.spinner('Fetching Data...'):
        feature = predict_weather()
with c3:
    compbutton = st.button("Obtain Location + Comparison Metrics")
if compbutton == True:
    with st.spinner('Fetching Data...'):
        predict_weather(compare = True, location = compare_location, compmetrics = predict_weather())