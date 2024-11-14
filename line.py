import pydeck as pdk
import pandas 
# DATA_URL = {
#     "AIRPORTS": "https://raw.githubusercontent.com/visgl/deck.gl-data/master/examples/line/airports.json",
#     "FLIGHT_PATHS": "https://raw.githubusercontent.com/visgl/deck.gl-data/master/examples/line/heathrow-flights.json",  # noqa
# }

INITIAL_VIEW_STATE = pdk.ViewState(latitude=47.65, longitude=7, zoom=4.5, max_zoom=16, pitch=50, bearing=0)

df_with_routes = pandas.read_csv("./dataset/Frequent_trip_with_routes.csv")  # Adjust path if needed
df_stops = pandas.read_excel("./dataset/FLEXI_bus_stops.xls")

# print(df_with_routes["route"].apply(eval)) 

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
    radius_scale=20,
    get_position=["longitude", "latitude"],
    get_fill_color=[255, 140, 0],
    get_radius=10,
    pickable=True,
)

# line_layer = pdk.Layer(
#     "LineLayer",
#     line_data,
#     get_source_position="start",
#     get_target_position="end",
#     get_color=GET_COLOR_JS,
#     get_width=2,
#     highlight_color=[255, 255, 0],
#     picking_radius=10,
#     auto_highlight=True,
#     pickable=True,
# )

line_layer = pdk.Layer(
        "LineLayer",
        data=line_data,
        get_source_position="start",
        get_target_position="end",
        get_color=JS_COLOR,
        get_width=3,
        width_scale=0.5,
        highlight_color=[255, 255, 0],
        auto_highlight=True,
        opacity=0.8,
        pickable=True
    )

layers = [ line_layer]

r = pdk.Deck(layers=layers, initial_view_state=INITIAL_VIEW_STATE, map_style="dark")
r.show()
