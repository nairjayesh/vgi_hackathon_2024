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

    deck = pdk.Deck(
        layers=[heatmap_layer], 
        initial_view_state=INITIAL_VIEW_STATE,
        map_style="road"
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