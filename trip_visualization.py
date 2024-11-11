import pandas 
import pydeck 
import streamlit 
import time 
import numpy 

# 0_ DATA PREPROCESSING 
table1 = pandas.read_excel("./FLEXI_bus_stops.xls")
table2 = pandas.read_excel("./FLEXI_trip_data.xls")

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
merged_data['Pickup Day'] = merged_data['Actual Pickup Time'].dt.dayofweek  # 0 = Monday, 1= Tuesday, 2 = Wednesday ... 

origin_destination_pair = merged_data.groupby(['pickup_index', 'pickup_name', 'pickup_district', 'pickup_latitude', 'pickup_longitude', 'index_dropoff', \
                                               'name_dropoff', 'district_dropoff', 'latitude_dropoff', 'longitude_dropoff']) \
                                            .size() \
                                            .reset_index(name="Frequency") \
                                            .sort_values(by='Frequency', ascending=False)


# 1_ TRIP DATA VISUALIZATION 

df_test = origin_destination_pair #.nlargest(10, 'Frequency') 
max_frequency = df_test["Frequency"].max()
min_frequency = df_test["Frequency"].min() 
df_test["height"] = df_test["Frequency"] / (max_frequency) * 2
# FIRST CREATE A MAP 

streamlit.title("Trip Vislualization with Frequency threshold")
frequency_threshold = streamlit.slider("Frequency", min_frequency, max_frequency, min_frequency)

filtered_df = df_test[df_test["Frequency"] >= frequency_threshold]


# CREATE A MINIMAL VIEW STATE: 
INITIAL_VIEW_STATE = pydeck.ViewState(
    latitude=filtered_df["pickup_latitude"].mean(), 
    longitude=filtered_df["pickup_longitude"].mean(),
    zoom=11, 
    pitch=60,
    bearing=180 
)


# CREATE A MINIMAL ARCLAYER 
arc_layer = pydeck.Layer(
    "ArcLayer", 
    data=filtered_df, 
    get_source_position=["pickup_longitude", "pickup_latitude"], 
    get_target_position=["longitude_dropoff", "latitude_dropoff"],
    get_height="height", 
    get_width=1,
    get_tilt=15, 
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
    map_style="dark", 
    tooltip=tooltip
) 

streamlit.pydeck_chart(deck)

# 1.2 BRUSHING EFFECT FOR PATTERNS 

# def filter_brush(data, brush_radius):
#     """Filter arcs based on proximity to a central point."""
#     center = numpy.mean([arc['source'] for arc in data], axis=0)  # Use central point of dataset
#     filtered_data = [
#         arc for arc in data if numpy.linalg.norm(numpy.array(arc['source']) - center) < brush_radius
#     ]
#     return filtered_data

# filtered_arcs =  filter_brush(filtered_df, brush_radius=100_000) 

# inFlowColor = [35, 181, 184]
# outFlowColor = [166, 3, 3]

# scatter_layer = pydeck.Layer(
#     "ScatterplotLayer",
#     data=filtered_arcs,
#     get_position="target",
#     get_radius=5000,
#     get_fill_color=inFlowColor,
#     pickable=True,
# )

# 2_ TRAVEL PATTERNS WITH RESPECT TO TIME OF THE DAY: 
# YOU CAN AGIAIN REPEAT arc (boring) -> TRY TRIP ROUTE 

