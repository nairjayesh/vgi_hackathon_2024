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
    # route_data
    table_4 = pandas.read_excel(Path("./dataset/route_data.xlsx"))

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

    # to only take trip completed data
    validated_trip_merged_data = merged_data[merged_data['Passenger status'] != 'Cancelled'] # TODO: RENAME variable to represent the state change: Only valid trips taken
    canceled_trip_merged_data  = merged_data[merged_data['Passenger status'] == 'Cancelled']

    # merge weather_data
    validated_trip_merged_data = validated_trip_merged_data.merge(
        table_3[['booking_id', 'weather_max_temp', 'weather_min_temp', 'weather_status', 'weather_chance_of_precipitation']],
        how='left',  # 'left' join to keep all rows in 1st df and add only weather data from 2nd df
        left_on='Booking ID',
        right_on='booking_id'
    )
    # merge route_data
    validated_trip_merged_data = validated_trip_merged_data.merge(
        table_4[['Booking ID', 'route', 'timestamps']],
        how='left',
        on='Booking ID',
    )
    validated_trip_merged_data = validated_trip_merged_data.drop(columns=['booking_id'])
    return (validated_trip_merged_data, 
            canceled_trip_merged_data)


@streamlit.cache_data
def load_bus_data():
    return pandas.read_excel(Path("./dataset/FLEXI_bus_stops.xls"))

@streamlit.cache_data
def load_mapped_dataset():
    return pandas.read_excel(Path("./dataset/weather_data.xlsx"))
