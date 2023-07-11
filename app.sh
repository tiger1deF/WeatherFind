#!/bin/bash
dir=$PWD
python -m virtualenv "$dir"
. bin/activate
pip install matplotlib pandas streamlit geopy meteostat torch watchdog
streamlit run "$dir/Download Weather.py"