import pandas
from pathlib import Path
import os
import streamlit

@streamlit.cache_data
def load_dataset():
    # # 0_ DATA PREPROCESSING 
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