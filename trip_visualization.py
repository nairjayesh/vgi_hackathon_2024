import pandas 
import pydeck 
import streamlit 
import time 
import numpy 


# Set Streamlit to use the full width of the page
streamlit.set_page_config(layout="wide")

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
merged_data['Dropoff Hour'] = merged_data['Actual Dropoff Time'].dt.hour
merged_data['Pickup Day'] = merged_data['Actual Pickup Time'].dt.dayofweek  # 0 = Monday, 1= Tuesday, 2 = Wednesday ... 

origin_destination_pair = merged_data.groupby(['pickup_index', 'pickup_name', 'pickup_district', 'pickup_latitude', 'pickup_longitude', 'index_dropoff', \
                                               'name_dropoff', 'district_dropoff', 'latitude_dropoff', 'longitude_dropoff']) \
                                            .size() \
                                            .reset_index(name="Frequency") \
                                            .sort_values(by='Frequency', ascending=False)


# 1_ TRIP DATA VISUALIZATION 

def trip_data_viz():
    """
    We use an arc layer here to understand trips wrt frequency, below we will use an alternate 
    method to understand trip wrt time, but this can be used as well. 

    Ignore 1.2 It's still an experimental visualization to try in case we want later. 

    To run, just type in the CLI: 
    streamlit run trip_visualization.py 

    Play with the Frequency slider to see how the trips are scheduled. 

    NOTE: When we see the figures, we might think --> Eg: From Kinding to Bilengries: Why did we get 100? 
    Is it a popular route for daily commute? -- what's our daily average like? (V. V. Interesting to answer)
    Or do we have a specific period when most of the ride happened? 
    """

    df_test = origin_destination_pair #.nlargest(10, 'Frequency') 
    max_frequency = df_test["Frequency"].max()
    min_frequency = df_test["Frequency"].min() 
    df_test["height"] = df_test["Frequency"] / (max_frequency) * 2
    # FIRST CREATE A MAP 


    streamlit.markdown("<h1 style='text-align: center;'>Trip Visualization and Data Analysis</h1>", unsafe_allow_html=True)


    col1, col2 = streamlit.columns([2.8, 1.2])

    with col1:
        streamlit.subheader("Trip Vislualization with Frequency threshold")
        frequency_threshold = streamlit.slider("Frequency", min_frequency, max_frequency, min_frequency)

        filtered_df = df_test[df_test["Frequency"] >= frequency_threshold]


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

    with col2:
        # streamlit.header("Top 5 Pickup-Dropoff Pairs")
        streamlit.subheader("Top 5 Pickup-Dropoff Pairs")
        top_5_pairs = origin_destination_pair.head(5)
        streamlit.write("")
        streamlit.write("")
        streamlit.write("")
        streamlit.write("")
        streamlit.write("")
        streamlit.write("")
        streamlit.write("")
        streamlit.write("")
        streamlit.write("")
        streamlit.write("")
        streamlit.table(
            top_5_pairs[['pickup_name', 'name_dropoff', 'Frequency']].rename(
                columns={
                    'pickup_name': 'Pickup Location',
                    'name_dropoff': 'Dropoff Location'
                }
            )
        )


# Initial Demand HeatMap wrt TIME (Spatial and temporal component)

def heatmap_wrt_time():
    df2 = merged_data #df used in this function

    pickup_data = df2[['pickup_name', 'pickup_latitude', 'pickup_longitude', 'Pickup Hour']].copy()
    pickup_data['type'] = 'pickup'  # Marking as pickup
    pickup_data.rename(columns={'pickup_name': 'Stop_Name', 'pickup_latitude': 'latitude', 'pickup_longitude': 'longitude', \
                                'Pickup Hour': 'Hour'}, inplace=True)


    dropoff_data = df2[['name_dropoff','latitude_dropoff', 'longitude_dropoff', 'Dropoff Hour']].copy()
    dropoff_data['type'] = 'dropoff'  # Marking as dropoff
    dropoff_data.rename(columns={'name_dropoff': 'Stop_Name', 'latitude_dropoff': 'latitude', 'longitude_dropoff': 'longitude', \
                                 'Dropoff Hour': 'Hour'}, inplace=True)

    # Combine both pickup and dropoff data into one DataFrame
    combined_data = pandas.concat([pickup_data, dropoff_data], ignore_index=True)
    combined_data.loc[:,'demand'] = (combined_data['latitude'] + combined_data['longitude']).apply(lambda x: x % 100)

    # selected_hour = streamlit.slider(
    # "Select Hour of the Day",
    # min_value=0,
    # max_value=23,
    # value=6,  # Default hour
    # step=1,
    # format="Hour: %d"
    # )

    # # Filter data based on the selected hour (pickup or dropoff)
    # filtered_data = combined_data[combined_data['Hour'] == selected_hour]

    # # Aggregate the data based on the filtered time and location
    # filtered_data['demand'] = filtered_data.groupby(['latitude', 'longitude', 'Hour'])['latitude'].transform('count')

    INITIAL_VIEW_STATE = pydeck.ViewState(
        latitude=df2["pickup_latitude"].mean(), 
        longitude=df2["pickup_longitude"].mean(),
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

    streamlit.pydeck_chart(deck)
            

# Mapping options to their respective functions
visualization_mapping = {
    "Heatmap": heatmap_wrt_time,
    "Trip Data Information": trip_data_viz,
    #"Line Chart": render_line_chart
}

# Dropdown for selecting visualization
viz_option = streamlit.selectbox("Choose a visualization", list(visualization_mapping.keys()))

# Render the selected visualization
visualization_mapping[viz_option]()


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