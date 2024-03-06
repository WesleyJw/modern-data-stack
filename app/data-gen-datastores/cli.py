"""
CLI that uses Typer to build the command line interface.

python cli.py --help

python cli.py all parquet
python cli.py mssql json
python cli.py postgres json
python cli.py mongodb json
python cli.py redis json
"""

import typer

from rich import print
from main import MinioStorage
from dotenv import load_dotenv

load_dotenv()


def main(dstype: str, format_type: str):
    """
    :param dstype: The type of data storage to write the file to. It can be one of the following options: "mssql", "postgres", "mongodb", "redis", or "all".
    :param format_type: The format of the file to be written.
    :return: None

    This method writes a file to the specified data storage type based on the provided parameters. It uses the `MinioStorage` class to perform the file write operation.

    If `dstype` is "mssql", the file will be written to a Microsoft SQL Server data storage. If `dstype` is "postgres", the file will be written to a PostgreSQL data storage. If `dstype
    *` is "mongodb", the file will be written to a MongoDB data storage. If `dstype` is "redis", the file will be written to a Redis data storage. If `dstype` is "all", the file will be
    * written to all available data storages.
    """

    if dstype == "mssql":
        print(MinioStorage().write_file(ds_type="mssql", format_type=format_type))
    elif dstype == "postgres":
        print(MinioStorage().write_file(ds_type="postgres", format_type=format_type))
    elif dstype == "mongodb":
        print(MinioStorage().write_file(ds_type="mongodb", format_type=format_type))
    elif dstype == "redis":
        print(MinioStorage().write_file(ds_type="redis", format_type=format_type))
    elif dstype == "all":
        print(MinioStorage().write_file(ds_type="mssql", format_type=format_type))
        print(MinioStorage().write_file(ds_type="postgres", format_type=format_type))
        print(MinioStorage().write_file(ds_type="mongodb", format_type=format_type))


if __name__ == "__main__":
    typer.run(main)
