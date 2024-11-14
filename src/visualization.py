import pydeck as pdk
import streamlit as st
import pandas as pd
import src.data_preprocessing as dp
from src.utility import get_icon_url

def create_map1(data, start_time, end_time, frequency_threshold, days_of_week):
    data = data[(data["Pickup Hour"] >= start_time) & (data["Dropoff Hour"] <= end_time)]
    if days_of_week:
        data = data[data["Actual Pickup Time"].dt.strftime('%A').isin(days_of_week)]

    origin_destination_pair = data.groupby(['pickup_index', 'pickup_name', 'pickup_district', 'pickup_latitude', 'pickup_longitude', 'index_dropoff', \
                                            'name_dropoff', 'district_dropoff', 'latitude_dropoff', 'longitude_dropoff']) \
                                  .size() \
                                  .reset_index(name="Frequency") \
                                  .sort_values(by='Frequency', ascending=False)

    max_frequency = origin_destination_pair["Frequency"].max()
    origin_destination_pair["height"] = origin_destination_pair["Frequency"] / max_frequency * 2
    filtered_df = origin_destination_pair[origin_destination_pair["Frequency"] >= frequency_threshold]

    INITIAL_VIEW_STATE = pdk.ViewState(
        latitude=filtered_df["pickup_latitude"].mean(), 
        longitude=filtered_df["pickup_longitude"].mean(),
        zoom=11, 
        pitch=50,
        bearing=180 
    )

    arc_layer = pdk.Layer(
        "ArcLayer",
        data=filtered_df,
        get_source_position=["pickup_longitude", "pickup_latitude"],
        get_target_position=["longitude_dropoff", "latitude_dropoff"],
        get_height="height",
        get_width=3,
        get_tilt=25,
        get_source_color=[255, 0, 0, 140],
        get_target_color=[0, 0, 255, 140],
        pickable=True,
        auto_highlight=True,
    )

    tooltip = {
        "html": "<b>Frequency:</b> {Frequency}<br/>"
                "<b>Pickup:</b> [{pickup_name}]<br/>"
                "<b>Dropoff:</b> [{name_dropoff}]",
        "style": {
            "backgroundColor": "rgba(255, 255, 255, 0.6)",  # White background for a clean look
            "background": "linear-gradient(145deg, rgba(243, 244, 246, 0.6), rgba(226, 232, 240, 0.6))",  # Soft gradient for a modern feel
            "color": "#333333",  # Darker text for better readability
            "fontFamily": "Helvetica Neue, Arial, sans-serif",  # Apple-like font
            "fontSize": "14px",  # Slightly larger text
            "borderRadius": "12px",  # Rounded corners for a smooth look
            "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.1)",  # Soft shadow for depth
            "padding": "10px 15px",  # More padding for readability
            "border": "none",  # Remove border for a cleaner design
            "textAlign": "left",  # Center the text for balance
        }
    }
    deck = pdk.Deck(layers=[arc_layer], initial_view_state=INITIAL_VIEW_STATE, map_style="road", tooltip=tooltip)

    st.pydeck_chart(deck)

    st.title("Top 5 Pickup-Dropoff Pairs")
    top_5_pairs = origin_destination_pair.head(5)
    st.table(
        top_5_pairs[['pickup_name', 'name_dropoff', 'Frequency']].rename(
            columns={
                'pickup_name': 'Pickup Location',
                'name_dropoff': 'Dropoff Location'
            }
        )
    )


def demand_heatmap(dataset, time_hour, day_of_week):
    demand_data = dataset[dataset['Pickup Hour'] == time_hour]
    day_mapping = {
    "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
    "Friday": 4, "Saturday": 5, "Sunday": 6
    }
    if day_of_week:
        # Convert selected day names to their corresponding numeric values
        selected_days = [day_mapping[day] for day in day_of_week]
        # Filter the DataFrame
        demand_data = demand_data[demand_data["Pickup Day"].isin(selected_days)] 

    demand_data = demand_data.groupby(['pickup_index', 'pickup_name', 'pickup_district', 'pickup_latitude', 'pickup_longitude',\
                                        ])\
                                        .agg(
                                            No_of_Passengers = ('Passengers', 'sum'), 
                                            Pickup_count=('Passengers', 'size')
                                        ) \
                                        .reset_index() \
                                        .sort_values(by='No_of_Passengers', ascending=False)
    
    # demand_data[['Occupancy_rate', 'Occupancy_icon']] = demand_data['No_of_Passengers'].apply(lambda x: pd.Series(get_icon_url(x)))
    demand_data['Occupancy_icon'] = demand_data['No_of_Passengers'].apply(get_icon_url)

    print(demand_data.head())

    INITIAL_VIEW_STATE = pdk.ViewState(
        latitude=dataset["pickup_latitude"].mean(), 
        longitude=dataset["pickup_longitude"].mean(),
        zoom=11, 
        pitch=40,
        bearing=30
    )

    color_range = [
        [0, 0, 255],      # Blue
        [0, 255, 255],    # Cyan
        [0, 255, 0],      # Green
        [255, 255, 0],    # Yellow
        [255, 0, 0],      # Red
    ]

    heatmap_layer = pdk.Layer(
        "HeatmapLayer",
        demand_data,
        get_position=["pickup_longitude", "pickup_latitude"],  
        get_weight="No_of_Passengers",  
        radius_pixels=50,  
        intensity=2,  
        threshold=0.1, 
        color_range=color_range 
    )

    scatterplot_layer = pdk.Layer(
        "ScatterplotLayer",
        demand_data,
        get_position=["pickup_longitude", "pickup_latitude"],  # Longitude and Latitude for scatter points
        get_fill_color="[200, 30, 0, 160]",  # Red color with some opacity (RGBA)
        get_radius=150,  # Radius of each scatter point
        pickable=True,  # Make the points interactive for selection
        opacity=0  # Set opacity to make it semi-transparent
    )

                    # <img src='""" + get_icon_url("{No_of_Passengers}") + """'
                    # alt='icon' width='16' height='16'><br/>
                    #                <b><span style='vertical-align: middle, margin-left: 5px;'> {Occupancy_rate}</span><br/>
    # get_icon_url(No_of_Passengers)
    print(demand_data.head())
    # print(demand_data.columns)
    # print(demand_data['No_of_Passengers'])
    tooltip = {
        "html": """<b>Stop Name :</b> {pickup_name}<br/>
                <img src='{occupancy_icon}' 
                alt='icon' width='16' height='16'><br/>
                <b>Passengers:</b> {No_of_Passengers}<br/>""",
        "style": {
            "backgroundColor": "rgba(255, 255, 255, 0.6)",  # White background for a clean look
            "background": "linear-gradient(145deg, rgba(243, 244, 246, 0.6), rgba(226, 232, 240, 0.6))",  # Soft gradient for a modern feel
            "color": "#333333",  # Darker text for better readability
            "fontFamily": "Helvetica Neue, Arial, sans-serif",  # Apple-like font
            "fontSize": "14px",  # Slightly larger text
            "borderRadius": "12px",  # Rounded corners for a smooth look
            "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.1)",  # Soft shadow for depth
            "padding": "10px 15px",  # More padding for readability
            "border": "none",  # Remove border for a cleaner design
            "textAlign": "left",  # Center the text for balance
        }
    }

    deck = pdk.Deck(
        layers=[heatmap_layer, scatterplot_layer], 
        initial_view_state=INITIAL_VIEW_STATE,
        map_style="road",
        tooltip=tooltip
    )

    map_col, table_col = st.columns([3, 1])
    with map_col:
        st.pydeck_chart(deck)

    with table_col:
        st.markdown('<h2 style="font-size: 24px; color: #4CAF50;">Most Demanded Stops</h2>', unsafe_allow_html=True)
        top_5_pairs = demand_data.head()
        st.table(
            top_5_pairs[['pickup_name', 'Pickup_count']].rename(
                columns={
                    'pickup_name': 'Stop Name',
                    'Pickup_count': 'Number of Pickups'
                }
            )
        )

    st.markdown("""
        <style>
        .stSelectbox>div>div>input {
            border: 1px solid #4CAF50;
            border-radius: 5px;
            padding: 8px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("Pick a Bus Stop for more information")
    pickup_name = st.selectbox("Select a Pickup Stop", demand_data['pickup_name'].unique())
    selected_info = demand_data[demand_data['pickup_name'] == pickup_name]
    if not selected_info.empty:
        selected_info = selected_info.iloc[0]  # Get the first row if any data is found
        st.write(f"**Stop Name**: {selected_info['pickup_name']}")
        st.write(f"**District**: {selected_info['pickup_district']}")
        st.write(f"**Number of Passengers**: {selected_info['No_of_Passengers']}")
        st.write(f"**Number of Pickups**: {selected_info['Pickup_count']}")
    else:
        st.write("No data found for the selected stop.")

def create_map3(route_dataset, start_time, end_time, days_of_week):
    df_stops = dp.load_bus_data()

    # filter by input
    route_dataset = route_dataset[(route_dataset["Pickup Hour"] >= start_time) & (route_dataset["Dropoff Hour"] <= end_time)]
    if days_of_week:
        route_dataset = route_dataset[route_dataset["Actual Pickup Time"].dt.strftime('%A').isin(days_of_week)]
    # for testing - only taking first 5 rows
    df_with_routes = route_dataset.iloc[0:5]
    df_with_routes = df_with_routes.groupby(['pickup_index', 'pickup_name', 'pickup_district', 'pickup_latitude', 'pickup_longitude', 'index_dropoff', \
                                            'name_dropoff', 'district_dropoff', 'latitude_dropoff', 'longitude_dropoff', 'route', 'timestamps']) \
                                  .size() \
                                  .reset_index(name="Frequency") \
                                  .sort_values(by='Frequency', ascending=False)

    line_data = []
    MAX_FREQ = int(df_with_routes["Frequency"].max())
    for path, frequency in zip(df_with_routes["route"].apply(eval), df_with_routes["Frequency"]):  # Convert route strings to lists
        total_segments = len(path) - 1
        for i in range(total_segments):
            start = path[i] + [i]
            end = path[i + 1] + [i]
                
            line_data.append({
                    "start": start,
                    "end": end,
                    "Frequency": frequency, 
                    "color_val": (frequency / MAX_FREQ) * 10      # Segment index for fading  # Total segments to normalize
            })

    # # # RGBA value generated in Javascript by deck.gl's Javascript expression parser
    # GET_COLOR_JS = [
    #     "255 * (1 - segment_index / total_segments)",   # Red fades out along the path
    #     "128 * (segment_index / total_segments)",       # Green increases
    #     "255 * (segment_index / total_segments)",       # Blue increases
    #     "255 * (1 - segment_index / total_segments)"    # Alpha decreases
    # ]

    JS_COLOR = [
        "50 * color_val",        # Red intensity based on frequency
        "255 * (1 - color_val)",   # Subdued green for lower frequencies
        "50 * (1 - color_val)",   # Subdued blue for lower frequencies
        "255 * color_val"         # Opacity based on frequency (fades lower frequencies)
    ]

    scatterplot = pdk.Layer(
        "ScatterplotLayer",
        df_stops,
        radius_scale=4,
        get_position=["longitude", "latitude"],
        get_fill_color=[0, 0, 0],
        get_radius=10,
        pickable=True,
    )

    tooltip = {
        "html": "</b>{name}<br/>",
        "style": {
            "backgroundColor": "black",
            "color": "white",
            "fontSize": "12px",
            "padding": "5px", 
            "borderRadius": "5px"
        }
    }

    line_layer = pdk.Layer(
            "LineLayer",
            data=line_data,
            get_source_position="start",
            get_target_position="end",
            get_color=JS_COLOR,
            get_width=5,
            width_scale=0.5,
            highlight_color=[255, 255, 0],
            auto_highlight=True,
            opacity=0.8,
        )

    layers = [scatterplot, line_layer]

    INITIAL_VIEW_STATE = pdk.ViewState(latitude=df_with_routes["pickup_latitude"].mean(), longitude=df_with_routes["pickup_longitude"].mean(), zoom=11, pitch=50)

    r = pdk.Deck(layers=layers, initial_view_state=INITIAL_VIEW_STATE, map_style="light", tooltip=tooltip)
    st.pydeck_chart(r)

    ''' legend - seems not working, pydeck does not allow legends in map, next option is to overlay above map using streamlit '''
    # legend_html = """
    # <div style="position: absolute; top: 20px; left: 20px; background: rgba(0, 0, 0, 0.7); color: white; padding: 10px; border-radius: 5px; z-index: 1000;">
    #     <h3>Legend</h3>
    #     <p><strong>Black dots</strong> represent bus stops.</p>
    #     <p><strong>Size of the dot</strong> indicates the number of occurrences.</p>
    # </div>
    # """
    # # Render the legend as part of the Streamlit UI, positioned above the map
    # st.markdown(legend_html, unsafe_allow_html=True)
