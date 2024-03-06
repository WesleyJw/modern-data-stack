import os
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from datetime import datetime
from pycpfcnpj import gen

load_dotenv()

pd.set_option('display.max_rows', 100000)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

rides_files_location = os.getenv("RIDES_FILES")


class Rides:
    """
    A class that provides methods for retrieving ride data.
    """

    def __init__(self):
        """
        Initialize the Rides object.
        """

        self.rides_files_location = rides_files_location

    def get_multiple_rows(self, gen_dt_rows):
        """
        Get multiple rows of ride data.

        Args:
            gen_dt_rows: The number of rows to generate.

        Returns:
            list: A list of dictionaries representing ride data.
        """

        current_datetime = datetime.now()
        formatted_timestamp = current_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        get_rides_data = pd.read_csv(self.rides_files_location)
        get_rides_data.columns = get_rides_data.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '')
        get_rides_data = get_rides_data.replace({np.nan: None})

        get_rides_data['user_id'] = np.random.randint(0, 1000, size=(len(get_rides_data), 1))
        # TODO get_rides_data['cpf'] = gen.cpf_with_punctuation()
        get_rides_data['vehicle_id'] = np.random.randint(0, 8219, size=(len(get_rides_data), 1))
        get_rides_data['dt_current_timestamp'] = formatted_timestamp
        get_rides_data['price'] = get_rides_data['price'].fillna(0)

        df = get_rides_data[['user_id', 'vehicle_id', 'time_stamp', 'source', 'destination', 'distance', 'price', 'surge_multiplier', 'id', 'product_id', 'name', 'cab_type', 'dt_current_timestamp']].sample(int(gen_dt_rows))
        return df.to_dict('records')
