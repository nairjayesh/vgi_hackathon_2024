import streamlit as st
from datetime import datetime
import time as t
import hydralit_components as hc
from datetime import time
import src.data_preprocessing as dp
import src.visualization as viz
import os
import streamlit as st
 
 
# streamlit page start config - dont remove this 
st.set_page_config(page_title="VGI Dashboard", page_icon="🚌", layout="wide")


def main():
    menu_data = [
        {'icon': "fas fa-map-marked-alt", 'label': "Demand Heatmap"},
        {'icon': "fas fa-chart-line", 'label': "Demand Trends"},
        {'icon': "fas fa-road", 'label': "Route Visualization"},
        {'icon': "fas fa-file-alt", 'label': "Generate Report"}
    ]

    
    menu_id = hc.nav_bar(menu_definition=menu_data, home_name='Project Overview')
    if menu_id == "Project Overview":
        st.title("About the Project")
        st.markdown("This initiative focuses on visualization of spatio-temporalbehavior of VGI-Flexi users as part VGI Challenge")
    elif menu_id == "Demand Trends":
        st.title("Ingolstadt Bus GPS Data")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            start_time_hour = st.slider("Pickup Time", min_value=0, max_value=23, value=0, step=2)
        with col2:
            end_time_hour = st.slider("Dropoff Time", min_value=0, max_value=23, value=23, step=2)
        with col3:
            frequency_threshold = st.slider("Frequency", min_value=0, max_value=100, value=10, step=1)
        with col4:
            days_of_week = st.multiselect("Days of Week", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])

        dataset = dp.load_dataset()
        viz.create_map1(dataset, start_time_hour, end_time_hour, frequency_threshold, days_of_week)

    elif menu_id == "Demand Heatmap":
        st.title("Mapping Demand: Uncovering VGI FLEXI Bus Stop Hotspots")
        col1, col2 = st.columns([3, 1])
        with col1:
            time_hour = st.slider("Time of Day", min_value=0, max_value=23, value=6, step=1, format="%d:00")
        with col2:
            # days_of_week = st.multiselect("Day(s) of Week", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
            # # If no days are selected, consider all days by default
            # if not days_of_week:
            #     days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            days_of_week = st.multiselect(
                    "Day(s) of Week", 
                    ["All", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                    default=["All"]
                )

                # If "All" is selected, select all days
            if "All" in days_of_week:
                days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


        dataset = dp.load_dataset()
        viz.demand_heatmap(dataset, time_hour, days_of_week)

    elif menu_id == "Route Visualization":
        st.title("VGI Flexi Route Map")
        col1, col2, col3 = st.columns(3)
        with col1:
            start_time_hour = st.slider("Pickup Time", min_value=0, max_value=23, value=0, step=2)
        with col2:
            end_time_hour = st.slider("Dropoff Time", min_value=0, max_value=23, value=23, step=2)
        with col3:
            days_of_week = st.multiselect("Days of Week", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])

        dataset = dp.load_dataset()
        viz.create_map3(dataset, start_time_hour, end_time_hour, days_of_week)


if __name__ == "__main__":
    main()
