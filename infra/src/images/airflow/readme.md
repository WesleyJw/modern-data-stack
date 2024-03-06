# docker 
```sh
docker build . -t owshq-apache-airflow:2.8.1 --platform linux/amd64
docker tag owshq-apache-airflow:2.8.1 owshq/owshq-apache-airflow:2.8.1
docker push owshq/owshq-apache-airflow:2.8.1
```