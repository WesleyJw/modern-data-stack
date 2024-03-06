# Data Gen DataStores

### connect to minio
```shell
mc alias set orion-minio-dev http://4.153.0.204 data-lake 12620ee6-2162-11ee-be56-0242ac120002
mc ls orion-minio-dev/landing
```

### write data to [interface]
```shell
python cli.py all parquet
python cli.py mssql json
python cli.py postgres json
python cli.py mongodb json
python cli.py redis json
```