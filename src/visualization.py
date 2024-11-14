import pandas as pd
import pydeck as pdk
import streamlit as st
import pandas as pd
import src.data_preprocessing as dp
from src.utility import get_icon_url

def create_map1(validated_trip_data, canceled_trip_data, start_time, end_time, frequency_threshold, days_of_week):
    day_mapping = {
    "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
    "Friday": 4, "Saturday": 5, "Sunday": 6
    }

    initial_latitude = validated_trip_data["pickup_latitude"].mean() 
    initial_longitude = validated_trip_data["pickup_longitude"].mean() 
    validated_trip_data = validated_trip_data[(validated_trip_data["Pickup Hour"] >= start_time) & (validated_trip_data["Dropoff Hour"] <= end_time)]
    canceled_trip_data = canceled_trip_data[(canceled_trip_data["Pickup Hour"] >= start_time) & (canceled_trip_data["Dropoff Hour"] <= end_time)]

    if days_of_week:
        selected_days = [day_mapping[day] for day in days_of_week]
        validated_trip_data = validated_trip_data[validated_trip_data["Pickup Day"].isin(selected_days)]
        canceled_trip_data = canceled_trip_data[canceled_trip_data["Pickup Day"].isin(selected_days)]
    validated_summary = validated_trip_data.groupby(['pickup_index', 'pickup_name', 'pickup_district', 'pickup_latitude', 'pickup_longitude', 'index_dropoff', \
                                            'name_dropoff', 'district_dropoff', 'latitude_dropoff', 'longitude_dropoff'
                                            ]).agg(
                                                Frequency=('Booking ID', 'size'),
                                                Total_Passengers=('Passengers', 'sum')
                                            ).reset_index().sort_values(by='Frequency', ascending=False)
    
    
    canceled_summary = canceled_trip_data.groupby([
        'pickup_index', 'pickup_name', 'pickup_district', 'pickup_latitude', 'pickup_longitude',
        'index_dropoff', 'name_dropoff', 'district_dropoff', 'latitude_dropoff', 'longitude_dropoff'
    ]).agg(
        Canceled_Count=('Booking ID', 'size')          # Count of canceled trips
    ).reset_index()

    combined_summary = pd.merge(
        validated_summary,
        canceled_summary,
        on=['pickup_index', 'pickup_name', 'pickup_district', 'pickup_latitude', 'pickup_longitude', 
            'index_dropoff', 'name_dropoff', 'district_dropoff', 'latitude_dropoff', 'longitude_dropoff'],
        how='left'  # Use left join to retain validated trips even if no cancellations
    )

    combined_summary['Canceled_Count'] = combined_summary['Canceled_Count'].fillna(0)

    combined_summary["Total_trip"] = (combined_summary["Frequency"] + combined_summary['Canceled_Count'] ).round(2)

    combined_summary['Cancellation_Rate'] = (combined_summary['Canceled_Count'] / 
                                             (combined_summary['Frequency'] + 
                                              combined_summary['Canceled_Count']) * 100
                                            ).round(2)

    max_frequency = combined_summary["Frequency"].max()
    combined_summary["height"] = combined_summary["Frequency"] / max_frequency * 2
    filtered_df = combined_summary[combined_summary["Frequency"] >= frequency_threshold]
    
    GET_WIDTH = [
        "Total_Passengers / 5" 
    ]

    tooltip = {
        "html": "<b>Completed Trips:</b> {Frequency}<br/>"
                "<b>Cancellation_rate:</b>{Cancellation_Rate} %<br/>"
                "<b>Total Bookings:</b>{Total_trip}<br/>"
                "<b>Pickup:</b> {pickup_name}<br/>"
                "<b>Dropoff:</b> {name_dropoff}<br/>"
                "<b>Passengers:</b>{Total_Passengers}"
                ,
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

    INITIAL_VIEW_STATE = pdk.ViewState(
            latitude=initial_latitude,
            longitude=initial_longitude,
            zoom=11, 
            pitch=50,
            bearing=180 
        )
    valid_rows = filtered_df.dropna(subset=["pickup_latitude", "pickup_longitude", "longitude_dropoff", "latitude_dropoff"]) 

    if  not valid_rows.empty:  
        arc_layer = pdk.Layer(
            "ArcLayer",
            data=filtered_df,
            get_source_position=["pickup_longitude", "pickup_latitude"],
            get_target_position=["longitude_dropoff", "latitude_dropoff"],
            get_height="height",
            get_width=GET_WIDTH,
            get_tilt=25,
            get_source_color=[255, 0, 0, 140],
            get_target_color=[0, 0, 255, 140],
            pickable=True,
            auto_highlight=True,
        )

        deck = pdk.Deck(layers=[arc_layer], initial_view_state=INITIAL_VIEW_STATE, map_style="road", tooltip=tooltip)

    else:
        empty_layer = pdk.Layer(
        "ScatterplotLayer",
        data=validated_summary,
        get_position=[0, 0],
        get_color=[0, 0, 0, 0],
        get_radius=0,
    )
    
        deck = pdk.Deck(
            layers=[empty_layer],
            initial_view_state=INITIAL_VIEW_STATE,
            map_style="road",
            tooltip=tooltip
        )    
        
    st.pydeck_chart(deck)
    
    #TODO: FIND A DEFAULT VALUE --> Where Viz looks good! 
    st.title("Top 5 Pickup-Dropoff Pairs")
    top_5_pairs = combined_summary.head(5)
    top_5_pairs['Frequency'] = top_5_pairs['Frequency'].astype(int)
    top_5_pairs['Cancellation_Rate'] = top_5_pairs['Cancellation_Rate'].round(2)
    top_5_pairs['Total_trip'] = top_5_pairs['Total_trip'].astype(int)

    st.table(
        top_5_pairs[['pickup_name', 'name_dropoff', 'Frequency', 'Cancellation_Rate', 'Total_trip']].rename(
            columns={
                'pickup_name': 'Pickup Location',
                'name_dropoff': 'Dropoff Location',
                'Frequency': 'Completed Trips',
                'Cancellation_Rate': 'Cancellation Rate (%)',
                'Total_trip': 'Total Bookings'
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
    #get_icon_url(No_of_Passengers)
    print(demand_data.head())
    print(demand_data.columns)
    print(demand_data['No_of_Passengers'])
    tooltip_html = """
                    <b>Stop Name :</b> {pickup_name}<br/>
                    <img src="{occupancy_icon}" alt="icon" width="16" height="16"><br/>
                    """
    tooltip = {
        "html": tooltip_html,
        "style": {
            "backgroundColor": "rgba(255, 255, 255, 0.6)",  
            "background": "linear-gradient(145deg, rgba(243, 244, 246, 0.6), rgba(226, 232, 240, 0.6))",  
            "color": "#333333",  
            "fontFamily": "Helvetica Neue, Arial, sans-serif", 
            "fontSize": "14px",  
            "borderRadius": "12px",  
            "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.1)",   
            "padding": "10px 15px",  
            "border": "none", 
            "textAlign": "left", 
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
