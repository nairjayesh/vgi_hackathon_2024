import pydeck as pdk
import streamlit as st
import src.data_preprocessing as dp

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
            "backgroundColor": "steelblue",
            "color": "white",
            "fontSize": "12px",
            "border": "1px solid gray"
        }
    }
    deck = pdk.Deck(layers=[arc_layer], initial_view_state=INITIAL_VIEW_STATE, map_style="road", tooltip=tooltip)

    st.pydeck_chart(deck)


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
        get_radius=100,  # Radius of each scatter point
        pickable=True,  # Make the points interactive for selection
        opacity=0.7  # Set opacity to make it semi-transparent
    )

    tooltip = {
        "html": """<b>Passengers:</b> {No_of_Passengers}<br/>
                <img src='data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2216%22%20height%3D%2216%22%3E%3Cg%20fill%3D%22none%22%20fill-rule%3D%22evenodd%22%3E%3Cpath%20fill%3D%22%23D7DCE1%22%20d%3D%22M0%2013c0%20.55.45%201%201%201h4c.583%200%201.024-.47%201.024-.988L6%209c0-1.037-.964-2-2-2H2C.931%207%200%207.996%200%209zm7.514-5L7.5%2014H10c.55%200%201-.482%201-1V9c0-1.134-.862-2-1.996-2h-.486a.985.985%200%200%200-1.004%201m4.988%200-.002%206%202.496-.016c.55%200%201.004-.466%201.004-.984V9c0-1.134-.866-2-2-2h-.526c-.55%200-.972.45-.972%201M3.016%205C3.836%205%204.5%204.337%204.5%203.484%204.5%202.664%203.837%202%203.016%202S1.5%202.663%201.5%203.484C1.5%204.337%202.195%205%203.016%205m5.5%200C9.336%205%2010%204.337%2010%203.484%2010%202.664%209.337%202%208.516%202S7%202.663%207%203.484C7%204.337%207.695%205%208.516%205m4.968%200C14.337%205%2015%204.337%2015%203.484%2015%202.664%2014.337%202%2013.484%202%2012.664%202%2012%202.663%2012%203.484%2012%204.337%2012.663%205%2013.484%205%22%2F%3E%3Cpath%20fill%3D%22%23646973%22%20d%3D%22M0%2013c0%20.55.45%201%201%201h4c.583%200%201.024-.47%201.024-.988L6%209c0-1.037-.964-2-2-2H2C.931%207%200%207.996%200%209zm7.514-5L7.5%2014H10c.55%200%201-.482%201-1V9c0-1.134-.862-2-1.996-2h-.486a.985.985%200%200%200-1.004%201M3.016%205C3.836%205%204.5%204.337%204.5%203.484%204.5%202.664%203.837%202%203.016%202S1.5%202.663%201.5%203.484C1.5%204.337%202.195%205%203.016%205m5.5%200C9.336%205%2010%204.337%2010%203.484%2010%202.664%209.337%202%208.516%202S7%202.663%207%203.484C7%204.337%207.695%205%208.516%205%22%2F%3E%3C%2Fg%3E%3C%2Fsvg%3E'
                alt='icon' width='16' height='16'><br/>
                <b>Pickup:</b> [{pickup_name}]<br/>""",
        "style": {
            "backgroundColor": "steelblue",
            "color": "white",
            "fontSize": "12px",
            "border": "1px solid gray"
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

def map3():
    pass