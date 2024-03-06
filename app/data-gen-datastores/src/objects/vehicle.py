from dotenv import load_dotenv
from datetime import datetime
import os
import pandas as pd
import numpy as np

load_dotenv()

pd.set_option('display.max_rows', 100000)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

vehicle_files_location = os.getenv("VEHICLE_FILES")


class Vehicle:
    """
    A class that provides methods for retrieving vehicle data.
    """

    def __init__(self):
        """
        Initialize the Vehicle object.
        """

        self.vehicle_files_location = vehicle_files_location

    def get_multiple_rows(self, gen_dt_rows):
        """
        Get multiple rows of vehicle data.

        Args:
            gen_dt_rows: The number of rows to generate.

        Returns:
            list: A list of dictionaries representing vehicle data.
        """

        current_datetime = datetime.now()
        formatted_timestamp = current_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        get_vehicle_data = pd.read_csv(self.vehicle_files_location)
        get_vehicle_data.columns = get_vehicle_data.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '')
        get_vehicle_data = get_vehicle_data.replace({np.nan: None})

        get_vehicle_data['id'] = np.random.randint(0, 8219, size=(len(get_vehicle_data), 1))
        get_vehicle_data['dt_current_timestamp'] = formatted_timestamp

        df = get_vehicle_data[['id', 'name', 'year', 'km_driven', 'fuel', 'seller_type', 'transmission', 'mileage', 'engine', 'max_power', 'torque', 'seats', 'dt_current_timestamp']].sample(int(gen_dt_rows))
        return df.to_dict('records')
