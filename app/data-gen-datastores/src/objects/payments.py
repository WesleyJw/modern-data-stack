import os
import pandas as pd
import numpy as np

from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

payments_file_location = os.getenv("PAYMENTS_FILES")


class Payments:
    """
    A class that provides methods for retrieving payment data.
    """

    def __init__(self):
        """
        Initialize the Payments object.
        """

        self.user_file_location = payments_file_location

    def get_multiple_rows(self, gen_dt_rows):
        """
        Get multiple rows of payment data.

        Args:
            gen_dt_rows: The number of rows to generate.

        Returns:
            list: A list of dictionaries representing payment data.
        """

        current_datetime = datetime.now()
        formatted_timestamp = current_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        get_user_data = pd.read_csv(self.user_file_location)
        get_user_data['dt_current_timestamp'] = formatted_timestamp
        get_user_data.columns = get_user_data.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(','').str.replace(')', '')
        get_user_data = get_user_data.replace({np.nan: None})

        user_output = get_user_data[
            [
                'user_id',
                'gender',
                'language',
                'race',
                'job_title',
                'city',
                'country',
                'currency',
                'currency_mode',
                'credit_card_type',
                'subscription_price',
                'time',
                'dt_current_timestamp'
            ]].head(int(gen_dt_rows))

        return user_output.to_dict('records')
