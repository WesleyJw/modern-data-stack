# Manifests Deployment

### helm repo
```sh
helm repo add apache-airflow https://airflow.apache.org
helm repo add elastic https://helm.elastic.co
helm repo update
```

### minio [deepstorage]
```shell
kubectl apply -f app-manifests/deepstorage/minio-operator.yaml
kubectl apply -f app-manifests/deepstorage/minio-tenant.yaml
```

### hive metastore [metastore]
```shell
kubectl apply -f app-manifests/metastore/hive-metastore.yaml
```

### trino [warehouse]
```shell
kubectl apply -f app-manifests/warehouse/trino.yaml
```

### airflow [orchestrator]
```shell
kubectl create secret generic airflow-fernet-key --from-literal=fernet-key='t5u8Dst5tkt1F5fwsxnfEwGfytY3Ry5KrP02B32mPxY=' --namespace orchestrator
kubectl apply -f git-credentials-secret.yaml --namespace orchestrator
kubectl apply -f app-manifests/orchestrator/airflow.yaml
```