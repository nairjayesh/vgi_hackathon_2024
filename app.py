import pandas 
import pydeck 
import time 
import numpy
from pathlib import Path
from copy import deepcopy
from datetime import datetime, time

# streamlit imports
import streamlit
import altair as alt
import plotly.express as px 
import streamlit_option_menu
from streamlit_option_menu import option_menu
import hydralit_components as hc


# config    
streamlit.set_page_config(
        page_title="VGI Dashboard",
        page_icon="🚌",
        layout="wide",
)


@streamlit.cache_data
def load_dataset():
    # 0_ DATA PREPROCESSING 
    table1 = pandas.read_excel(Path("./dataset/FLEXI_bus_stops.xls"))
    table2 = pandas.read_excel(Path("./dataset/FLEXI_trip_data.xls"))
    # weather_data
    table_3 = pandas.read_excel(Path("./dataset/weather_data.xlsx"))

    merged_data = table2.merge(table1, left_on="Pickup ID", right_on="index") \
                        .merge(table1, left_on="Dropoff ID", right_on="index", suffixes=('', '_dropoff')) \
                        .rename(columns={
                            "index": "pickup_index",
                            "name": "pickup_name",
                            "district": "pickup_district",
                            "latitude": "pickup_latitude",
                            "longitude": "pickup_longitude"
                        }) \
                        .drop(columns=["Pickup ID", "Dropoff ID"])

    merged_data['Actual Pickup Time'] = pandas.to_datetime(merged_data['Actual Pickup Time'])
    merged_data['Actual Dropoff Time'] = pandas.to_datetime(merged_data['Actual Dropoff Time'])
    merged_data['Pickup Hour'] = merged_data['Actual Pickup Time'].dt.hour
    merged_data['Dropoff Hour'] = merged_data['Actual Dropoff Time'].dt.hour
    merged_data['Pickup Day'] = merged_data['Actual Pickup Time'].dt.dayofweek  # 0 = Monday, 1= Tuesday, 2 = Wednesday ... 

    merged_data = merged_data[merged_data['Passenger status'] != 'Cancelled']
    
    # merge weather_data
    merged_data = merged_data.merge(
        table_3[['booking_id', 'weather_max_temp', 'weather_min_temp', 'weather_status', 'weather_chance_of_precipitation']],
        how='left',  # Use 'left' join to keep all rows in df1 and add weather data where available
        left_on='Booking ID',
        right_on='booking_id'
    )
    merged_data = merged_data.drop(columns=['booking_id'])
    return merged_data


def main():
    # menu definition
    menu_data = [
            {'icon': "far fa-chart-bar", 'label':"Visualization"},
            {'icon': "far fa-chart-bar", 'label':"Heat Map"},
            {'icon': "far fa-envelope", 'label':"Report"}
    ]
    menu_id = hc.nav_bar(menu_definition=menu_data,home_name='Home')
    if menu_id == "Home":
        streamlit.title("About the Project")
        streamlit.markdown("""As an integral part of AIMotion Bavaria, our initiative focuses on enhancing public transportation through the application of machine learning methodologies and simulations, leveraging authentic GPS data obtained from buses operating within Ingolstadt.""")
    elif menu_id == "Visualization":
        streamlit.title("Ingolstadt Bus GPS Data")

        # """
        # We use an arc layer here to understand trips wrt frequency, below we will use an alternate 
        # method to understand trip wrt time, but this can be used as well. 

        # Ignore 1.2 It's still an experimental visualization to try in case we want later. 

        # To run, just type in the CLI: 
        # streamlit run app.py 

        # Play with the Frequency slider to see how the trips are scheduled. 

        # NOTE: When we see the figures, we might think --> Eg: From Kinding to Bilengries: Why did we get 100? 
        # Is it a popular route for daily commute? -- what's our daily average like? (V. V. Interesting to answer)
        # Or do we have a specific period when most of the ride happened? 
        # """

        # calendar/slider - like selection box
        col1, col2, col3, col4 = streamlit.columns(4)
        with col1:
            start_time_hour = streamlit.slider("Pickup Time", min_value=0, max_value=23, value=0, step=2) # 300 sec = 5min
            start_time = time(start_time_hour, 0).hour
        with col2:
            end_time_hour = streamlit.slider("Dropoff Time", min_value=0, max_value=23, value=23, step=2)
            end_time = time(end_time_hour, 0).hour
        with col3:
            frequency_threshold = streamlit.slider("Frequency", min_value=0, max_value=100, value=10, step=1)
        with col4:
            days_of_week = streamlit.multiselect("Days of Week", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]) # , default=["Sunday", "Saturday"])

        # load dataset
        dataset = load_dataset()
        # filter wrt to chosen slider/calendar
        dataset = dataset[(dataset["Pickup Hour"] >= start_time) & (dataset["Dropoff Hour"] <= end_time)]
        if days_of_week:
            dataset = dataset[(dataset["Actual Pickup Time"].dt.strftime('%A').isin(days_of_week))]

        # grouping
        origin_destination_pair = dataset.groupby(['pickup_index', 'pickup_name', 'pickup_district', 'pickup_latitude', 'pickup_longitude', 'index_dropoff', \
                                                'name_dropoff', 'district_dropoff', 'latitude_dropoff', 'longitude_dropoff']) \
                                                .size() \
                                                .reset_index(name="Frequency") \
                                                .sort_values(by='Frequency', ascending=False)
        df_test = deepcopy(origin_destination_pair)
        max_frequency = df_test["Frequency"].max()
        min_frequency = df_test["Frequency"].min() 
        df_test["height"] = df_test["Frequency"] / (max_frequency) * 2
        filtered_df = df_test[df_test["Frequency"] >= frequency_threshold]

        # PyDeck
        # CREATE A MINIMAL VIEW STATE: 
        INITIAL_VIEW_STATE = pydeck.ViewState(
            latitude=filtered_df["pickup_latitude"].mean(), 
            longitude=filtered_df["pickup_longitude"].mean(),
            zoom=11, 
            pitch=50,
            bearing=180 
        )
        # CREATE A MINIMAL ARCLAYER 
        arc_layer = pydeck.Layer(
            "ArcLayer", 
            data=filtered_df, 
            get_source_position=["pickup_longitude", "pickup_latitude"], 
            get_target_position=["longitude_dropoff", "latitude_dropoff"],
            get_height="height", 
            get_width=3,
            get_tilt=25, 
            get_source_color=[255,0,0, 140], 
            get_target_color=[0,0,255,140],
            pickable=True, 
            auto_highlight=True,
        ) 
        tooltip = {
            "html": "<b>Frequency:</b> {Frequency}<br/>"
                    "<b>Pickup:</b> [{pickup_name}]<br/>"
                    "<b>Dropoff:</b> [{name_dropoff}]",
            "style": {
                "backgroundColor": "steelblue",
                "color": "white",
                "fontSize": "12px",
                "border": "1px solid gray"
            }
        }
        deck = pydeck.Deck(
            layers=[arc_layer],
            initial_view_state=INITIAL_VIEW_STATE,
            map_style="road", 
            tooltip=tooltip
        ) 
        streamlit.pydeck_chart(deck)
        
        streamlit.title("Top 5 Pickup-Dropoff Pairs")
        top_5_pairs = origin_destination_pair.head(5)
        streamlit.table(
            top_5_pairs[['pickup_name', 'name_dropoff', 'Frequency']].rename(
                columns={
                    'pickup_name': 'Pickup Location',
                    'name_dropoff': 'Dropoff Location'
                }
            )
        )
    elif menu_id == "Heat Map":
        # calendar/slider - like selection box
        col1, col2, col3 = streamlit.columns(3)
        with col1:
            start_time_hour = streamlit.slider("Pickup Time", min_value=0, max_value=23, value=0, step=2) # 300 sec = 5min
            start_time = time(start_time_hour, 0).hour
        with col2:
            end_time_hour = streamlit.slider("Dropoff Time", min_value=0, max_value=23, value=23, step=2)
            end_time = time(end_time_hour, 0).hour
        with col3:
            days_of_week = streamlit.multiselect("Days of Week", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]) # , default=["Sunday", "Saturday"])

        # load dataset
        dataset = load_dataset()
        # filter wrt to chosen slider/calendar
        dataset = dataset[(dataset["Pickup Hour"] >= start_time) & (dataset["Dropoff Hour"] <= end_time)]
        if days_of_week:
            dataset = dataset[(dataset["Actual Pickup Time"].dt.strftime('%A').isin(days_of_week))]

        # Initial Demand HeatMap wrt TIME (Spatial and temporal component)
        pickup_data = dataset[['pickup_name', 'pickup_latitude', 'pickup_longitude', 'Pickup Hour']].copy()
        pickup_data['type'] = 'pickup'  # Marking as pickup
        pickup_data.rename(columns={'pickup_name': 'stop_name', 'pickup_latitude': 'latitude', 'pickup_longitude': 'longitude', \
                                    'Pickup Hour': 'Hour'}, inplace=True)
        dropoff_data = dataset[['name_dropoff','latitude_dropoff', 'longitude_dropoff', 'Dropoff Hour']].copy()
        dropoff_data['type'] = 'dropoff'  # Marking as dropoff
        dropoff_data.rename(columns={'name_dropoff': 'stop_name', 'latitude_dropoff': 'latitude', 'longitude_dropoff': 'longitude', \
                                     'Dropoff Hour': 'Hour'}, inplace=True)
        # Combine both pickup and dropoff data into one DataFrame
        combined_data = pandas.concat([pickup_data, dropoff_data], ignore_index=True)
        combined_data.loc[:,'demand'] = (combined_data['latitude'] + combined_data['longitude']).apply(lambda x: x % 100)

        INITIAL_VIEW_STATE = pydeck.ViewState(
            latitude=dataset["pickup_latitude"].mean(), 
            longitude=dataset["pickup_longitude"].mean(),
            zoom=10.5, 
            pitch=5,
            bearing=55
        )
        heatmap_layer = pydeck.Layer(
            "HeatmapLayer",
            combined_data,
            get_position=["longitude", "latitude"],  
            get_weight="demand",  
            radius_pixels=50,  
            intensity=2,  
            threshold=0.1,  
        )
        # scatter_layer = pydeck.Layer(
        #     "ScatterplotLayer",
        #     combined_data,
        #     get_position=["longitude", "latitude"],  
        #     get_fill_color="color",  # We can use 'color' for the marker color
        #     get_radius=100,  # Adjust radius of the markers
        #     pickable=True,  # Allow the marker to be clickable
        # )
        deck = pydeck.Deck(
        layers=[heatmap_layer],
        initial_view_state=INITIAL_VIEW_STATE,
        map_style="road", 
        #tooltip=tooltip
        )

        # two columns for displaying on each side
        col_map, col_table = streamlit.columns([1, 1])
        with col_map:
            streamlit.pydeck_chart(deck)
        with col_table:
            streamlit.title("Most Demanded Stops")
            top_5_pairs = combined_data.head(10)
            streamlit.table(
                top_5_pairs[['stop_name', 'demand']].rename(
                    columns={
                        'Stop_Name': 'Stop Name',
                        'demand': 'Demand %',
                    }
                )
            )
    elif menu_id == "Report":
        streamlit.title("Report Dataset")

    # # 1.2 BRUSHING EFFECT FOR PATTERNS 

    # # def filter_brush(data, brush_radius):
    # #     """Filter arcs based on proximity to a central point."""
    # #     center = numpy.mean([arc['source'] for arc in data], axis=0)  # Use central point of dataset
    # #     filtered_data = [
    # #         arc for arc in data if numpy.linalg.norm(numpy.array(arc['source']) - center) < brush_radius
    # #     ]
    # #     return filtered_data

    # # filtered_arcs =  filter_brush(filtered_df, brush_radius=100_000) 

    # # inFlowColor = [35, 181, 184]
    # # outFlowColor = [166, 3, 3]

    # # scatter_layer = pydeck.Layer(
    # #     "ScatterplotLayer",
    # #     data=filtered_arcs,
    # #     get_position="target",
    # #     get_radius=5000,
    # #     get_fill_color=inFlowColor,
    # #     pickable=True,
    # # )

    # # 2_ TRAVEL PATTERNS WITH RESPECT TO TIME OF THE DAY: 
    # # YOU CAN AGIAIN REPEAT arc (boring) -> TRY TRIP ROUTE 


if __name__ == "__main__":
    main()
