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


def map2():
    pass

def map3():
    pass