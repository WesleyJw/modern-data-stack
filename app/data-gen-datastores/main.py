"""
SQL Server:
- Users
- Credit Card

Postgres:
- Payments
- Subscription
- Vehicle

MongoDB:
- Rides
- Users
- Stripe

Redis:
- Google Auth
- LinkedIn Auth
- Apple Auth
"""

import os
import uuid
import json
import random
import tempfile
import pyarrow as pa
import pandas as pd
import pyarrow.parquet as pq

from dotenv import load_dotenv
from io import BytesIO
from minio import Minio
from minio.error import S3Error
from datetime import datetime
from src.api import api_requests
from src.objects import users, rides, payments, vehicle

load_dotenv()

users = users.Users()
rides = rides.Rides()
payments = payments.Payments()
vehicle = vehicle.Vehicle()

api = api_requests.Requests()


class MinioStorage(object):
    """
    This class is used to write data into the MinIO server
    """

    def __init__(self, endpoint=None, access_key=None, secret_key=None, bucket_name=None):
        """
        Initialize the class with the provided parameters.

        :param endpoint: The endpoint URL for connecting to the storage service. Defaults to None.
        :type endpoint: str or None

        :param access_key: The access key for authentication. Defaults to None.
        :type access_key: str or None

        :param secret_key: The secret key for authentication. Defaults to None.
        :type secret_key: str or None

        :param bucket_name: The name of the bucket to be used for the storage service. Defaults to None.
        :type bucket_name: str or None

        """

        self.bucket_name = None
        self.client = None
        self.get_config_storage(endpoint, access_key, secret_key, bucket_name)

    def get_config_storage(self, endpoint, access_key, secret_key, bucket_name):
        """
        Get the configuration storage for the given endpoint, access key, secret key, and bucket name.

        :param endpoint: The endpoint URL for the Minio server. If not provided, it will be fetched from the environment variable "ENDPOINT".
        :param access_key: The access key for the Minio server. If not provided, it will be fetched from the environment variable "ACCESS_KEY".
        :param secret_key: The secret key for the Minio server. If not provided, it will be fetched from the environment variable "SECRET_KEY".
        :param bucket_name: The name of the bucket to be used for storing the configuration. If not provided, it will be fetched from the environment variable "LANDING_BUCKET".

        :return: None
        """

        endpoint = endpoint or os.getenv("ENDPOINT")
        access_key = access_key or os.getenv("ACCESS_KEY")
        secret_key = secret_key or os.getenv("SECRET_KEY")

        self.bucket_name = bucket_name or os.getenv("LANDING_BUCKET")
        self.client = Minio(endpoint, access_key, secret_key, secure=False)

    @staticmethod
    def create_dataframe(dt, ds_type, format_type, is_cpf=False):
        """
        :param dt: a list or array-like object representing the data to be converted into a DataFrame
        :param ds_type: a string representing the type of the data source
        :param format_type: a string representing the desired format of the output
        :param is_cpf: a boolean indicating whether to include the 'cpf' column in the DataFrame (default: False)
        :return: a tuple containing the created DataFrame or Table and the data source type

        This method takes in the specified parameters and creates a DataFrame using the provided data.
        It then adds two additional columns: 'user_id' and 'dt_current_timestamp', which are generated
        using the 'api.gen_user_id()' and 'api.gen_timestamp()' methods respectively.

        If the 'is_cpf' parameter is set to True, an additional column 'cpf' is added to the DataFrame.
        The 'cpf' column is generated using the 'api.gen_cpf()' method.

        If the 'format_type' parameter is set to "json" and the 'ds_type' parameter is not "redis", the DataFrame is
        converted to JSON format using the 'to_json()' method and encoded as UTF*-8.
        The encoded JSON data and the 'ds_type' are returned as a tuple.

        If the 'format_type' parameter is not "json", the DataFrame is converted to a Parquet table
        using the 'pa.Table.from_pandas()' method. The Parquet table and the 'ds_type' are returned * as a tuple.
        """

        pd_df = pd.DataFrame(dt)
        pd_df['user_id'] = api.gen_user_id()
        pd_df['dt_current_timestamp'] = api.gen_timestamp()

        if is_cpf:
            pd_df['cpf'] = [api.gen_cpf() for _ in range(len(pd_df))]

        if format_type == "json":
            if ds_type != "redis":
                json_data = pd_df.to_json(orient="records").encode('utf-8')
                return json_data, ds_type
        elif format_type == "parquet":
            parquet_table = pa.Table.from_pandas(pd_df)
            return parquet_table, ds_type

    def create_object_name(self, file_prefix, object_name, format_type, timestamp):
        """
        :param file_prefix: The prefix for the file or object name.
        :param object_name: The name of the object.
        :param format_type: The format type or extension of the object.
        :param timestamp: The timestamp to be appended to the object name.
        :return: The object name concatenating the input parameters using forward slashes.
        """

        return f"{file_prefix}/{object_name}/{format_type}/{timestamp}"

    def upload_data(self, data, object_name, ds_type, format_type):
        """
        :param data: The data to be uploaded.
        :param object_name: The name of the object in the S3 bucket.
        :param ds_type: The type of the data source.
        :param format_type: The format type of the data (json or parquet).
        :return: The result of the data upload.

        Uploads data to an S3 bucket based on the provided parameters. If the format type is "json",
        the data is uploaded as a json file. If the format type is "parquet", the data is uploaded * as a parquet file.
        """

        year, month, day, hour, minute, second = (datetime.now().strftime("%Y %m %d %H %M %S").split())
        file_loc_root_folder: str = "com.owshq.data"
        file_prefix = file_loc_root_folder + "/" + ds_type

        if format_type == "json":

            timestamp = f'{year}_{month}_{day}_{hour}_{minute}_{second}.json'
            object_name = self.create_object_name(file_prefix, object_name, format_type, timestamp)

            print(f"file location: {object_name}")

            try:
                json_buffer = BytesIO(data)

                put_data = self.client.put_object(
                    self.bucket_name,
                    object_name=object_name,
                    data=json_buffer,
                    length=len(data),
                    content_type='application/json'
                )

                return put_data

            except S3Error as exc:
                print(f"error occurred while uploading data, {exc}")

        elif format_type == "parquet":

            file_uuid = str(uuid.uuid4())
            object_name = self.create_object_name(file_prefix, object_name, format_type, file_uuid)

            print(f"file location: {object_name}")

            try:
                with tempfile.NamedTemporaryFile(suffix=".parquet") as temp_file:

                    pq.write_table(data, temp_file.name)
                    temp_file.seek(0)

                    put_data = self.client.put_object(
                        bucket_name="landing",
                        object_name=f"{object_name}.parquet",
                        data=temp_file,
                        length=os.path.getsize(temp_file.name),
                        content_type='application/octet-stream'
                    )

                    return put_data

            except S3Error as exc:
                print(f"error occurred while uploading data, {exc}")

    def write_file(self, ds_type: str, format_type: str):
        """
        Write data to a file based on the specified data source type and format type.

        :param ds_type: The type of data source. Valid values are "mssql", "postgres", "mongodb", "redis".
        :param format_type: The type of format to save the data.
        :return: If the data source type is "mssql", returns a tuple containing the upload results for the "users" and "credit_card" objects.
                 If the data source type is "postgres", returns a tuple containing the upload results for the "payments", "subscription", and "vehicle" objects.
                 If the data source type is "mongodb", returns a tuple containing the upload results for the "rides", "users", and "stripe" objects.
                 If the data source type is "redis", returns a tuple containing the upload results for the "google_auth", "linkedin_auth", and "apple_auth" objects.
        """

        gen_cpf = api.gen_cpf()

        params = {'size': 100}
        urls = {
            "users": "https://random-data-api.com/api/users/random_user",
            "credit_card": "https://random-data-api.com/api/business_credit_card/random_card",
            "subscription": "https://random-data-api.com/api/subscription/random_subscription",
            "stripe": "https://random-data-api.com/api/stripe/random_stripe",
            "google_auth": "https://random-data-api.com/api/omniauth/google_get",
            "linkedin_auth": "https://random-data-api.com/api/omniauth/linkedin_get",
            "apple_auth": "https://random-data-api.com/api/omniauth/apple_get"
        }

        if ds_type == "mssql":

            dt_users = users.get_multiple_rows(gen_dt_rows=100)
            dt_credit_card = api.api_get_request(url=urls["credit_card"], params=params)

            users_json, ds_type = self.create_dataframe(dt=dt_users, ds_type=ds_type, format_type=format_type, is_cpf=gen_cpf)
            credit_card_json, ds_type = self.create_dataframe(dt=dt_credit_card, ds_type=ds_type, format_type=format_type)

            return_users = self.upload_data(data=users_json, object_name="users", ds_type=ds_type, format_type=format_type)
            return_credit_card = self.upload_data(data=credit_card_json, object_name="credit_card", ds_type=ds_type, format_type=format_type)

            return return_users, return_credit_card

        elif ds_type == "postgres":
            dt_payments = payments.get_multiple_rows(gen_dt_rows=100)
            dt_subscription = api.api_get_request(url=urls["subscription"], params=params)
            dt_vehicle = vehicle.get_multiple_rows(gen_dt_rows=100)

            payments_json, ds_type = self.create_dataframe(dt=dt_payments, ds_type=ds_type, format_type=format_type)
            subscription_json, ds_type = self.create_dataframe(dt=dt_subscription, ds_type=ds_type, format_type=format_type)
            dt_vehicle_json, ds_type = self.create_dataframe(dt=dt_vehicle, ds_type=ds_type, format_type=format_type)

            return_payments = self.upload_data(data=payments_json, object_name="payments", ds_type=ds_type, format_type=format_type)
            return_subscription = self.upload_data(data=subscription_json, object_name="subscription", ds_type=ds_type, format_type=format_type)
            return_vehicle = self.upload_data(data=dt_vehicle_json, object_name="vehicle", ds_type=ds_type, format_type=format_type)

            return return_payments, return_subscription, return_vehicle

        elif ds_type == "mongodb":

            dt_rides = rides.get_multiple_rows(gen_dt_rows=100)
            dt_users = api.api_get_request(url=urls["users"], params=params)
            dt_stripe = api.api_get_request(url=urls["stripe"], params=params)

            rides_json, ds_type = self.create_dataframe(dt=dt_rides, ds_type=ds_type, format_type=format_type, is_cpf=gen_cpf)
            users_json, ds_type = self.create_dataframe(dt=dt_users, ds_type=ds_type, format_type=format_type, is_cpf=gen_cpf)
            stripe_json, ds_type = self.create_dataframe(dt=dt_stripe, ds_type=ds_type, format_type=format_type)

            return_rides = self.upload_data(data=rides_json, object_name="rides", ds_type=ds_type, format_type=format_type)
            return_users = self.upload_data(data=users_json, object_name="users", ds_type=ds_type, format_type=format_type)
            return_stripe = self.upload_data(data=stripe_json, object_name="stripe", ds_type=ds_type, format_type=format_type)

            return return_rides, return_users, return_stripe

        elif ds_type == "redis":
            user_id = random.randint(1, 10000)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

            dt_google_auth = api.api_get_request(url=urls["google_auth"], params=params)
            dt_google_auth["user_id"] = user_id
            dt_google_auth["timestamp"] = timestamp

            dt_linkedin_auth = api.api_get_request(url=urls["linkedin_auth"], params=params)
            dt_linkedin_auth["user_id"] = user_id
            dt_linkedin_auth["timestamp"] = timestamp

            dt_apple_auth = api.api_get_request(url=urls["apple_auth"], params=params)
            dt_apple_auth["user_id"] = user_id
            dt_apple_auth["timestamp"] = timestamp

            google_auth_json = json.dumps(dt_google_auth, ensure_ascii=False).encode('utf-8')
            linkedin_auth_json = json.dumps(dt_linkedin_auth, ensure_ascii=False).encode('utf-8')
            apple_auth_json = json.dumps(dt_apple_auth, ensure_ascii=False).encode('utf-8')

            return_google_auth = self.upload_data(data=google_auth_json, object_name="google_auth", ds_type=ds_type, format_type=format_type)
            return_linkedin_auth = self.upload_data(data=linkedin_auth_json, object_name="linkedin_auth", ds_type=ds_type, format_type=format_type)
            return_apple_auth = self.upload_data(data=apple_auth_json, object_name="apple_auth", ds_type=ds_type, format_type=format_type)

            return return_google_auth, return_linkedin_auth, return_apple_auth
