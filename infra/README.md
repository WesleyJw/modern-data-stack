# Infra

## How to create a kind cluster

To create a cluster with `kind` We need to write a `.yaml` file with cluster specifications. Save the following steps in a file named  `kind.yaml`.

```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
  - role: worker
  - role: worker
```

To create a cluster use:

```bsh
kind create cluster --name modern-stack --config kind.yaml
```

You can now check your cluster with:

```bsh
kubectl cluster-info --context kind-modern-stack

$ Kubernetes control plane is running at https://127.0.0.1:4624
$ CoreDNS is running at https://127.0.0.1:4624/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy
```

To further debug and diagnose cluster problems, use `kubectl cluster-info dump`.

Using `docker ps` you can see the created containers:

 ```sh
CONTAINER ID   IMAGE                  COMMAND                  CREATED       STATUS       PORTS                       NAMES
cd534bf47d15   kindest/node:v1.27.3   "/usr/local/bin/entr…"   3 hours ago   Up 3 hours   127.0.0.1:4624->644/tcp   modern-stack-control-plane
9d7e05f4589a   kindest/node:v1.27.3   "/usr/local/bin/entr…"   3 hours ago   Up 3 hours                               modern-stack-worker
20b2c317ebe2   kindest/node:v1.27.3   "/usr/local/bin/entr…"   3 hours ago   Up 3 hours                               modern-stack-worker2
```

To switching between contexts You can use `kubectl config use-context` with the name of a context that you want to use. To set kubectl context to `kind-modern-stack` use this:

```bsh
kubectl config use-context kind-modern-stack
```

We can see the nodes to created cluster: 

```bsh
kubectl get nodes
```

Some commands to interact with your cluster:

```bsh
# get context
$ kubectx
k3d-onion-dev
kind-modern-stack
minikube
```

## Creating PV and PVC

In Kubernetes, PersistentVolumes (PV) and PersistentVolumeClaims (PVC) manage persistent storage in a cluster. 

- **Persistent Volume (PV)**: A persistent storage unit, such as a hard disk or a cloud storage volume. The cluster administrator provisions a PV and can be used by multiple Pods. A PV has a lifecycle separate from the Pod that uses it.

- **PersistentVolumeClaim (PVC)**: It is a request for persistent storage made by a Pod. A PVC defines the amount of storage and the type of storage (e.g., SSD or HDD) that a Pod needs. When a Pod is created, Kubernetes finds a PV that matches the PVC and mounts the PV into the Pod. Kubernetes will automatically provision a new PV if there is no matching PV.

In summary, a PV is a resource that represents persistent storage in the cluster, and a PVC is a request for persistent storage made by a Pod. Kubernetes automatically manages the allocation and deallocation of PVs based on the PVCs and available PVs in the cluster.

The PV and PVC was provisioned to each cluster with the `pv-config.yaml` and `pvc-config.yaml` from `infra/src/private_volumes` directory.

Create this resources with:

```bash
kubectl apply -f pv-config.yaml pvc-config.yaml
```

Then We can use this resources in Our MinIO pods.

## Installation of DirectPV on Kind Cluster

[DirectPV](https://github.com/minio/directpv?tab=readme-ov-file) functions as a CSI driver specifically crafted for Direct Attached Storage, acting as a distributed persistent volume manager that sets it apart from storage systems like SAN or NAS. Its practicality extends to detecting, formatting, mounting, scheduling, and monitoring drives across multiple servers.

Direct-attached storage (DAS) refers to digital storage directly connected to the computer in use, in contrast to storage accessed via a computer network (such as network-attached storage). DAS comprises one or more storage units like hard drives, solid-state drives, and optical disc drives housed within an external enclosure. The term "DAS" is a retronym, highlighting the distinction from storage area network (SAN) and network-attached storage (NAS).

```sh
# Install DirectPV Krew plugin
kubectl krew install directpv

# Install DirectPV in your kubernetes cluster
kubectl directpv install

# Get information of the installation
kubectl directpv info

# Add drives

## Probe and save drive information to drives.yaml file.
kubectl directpv discover

## Initialize selected drives.
## you can create a yaml file with the configs
cat drives.yaml
kubectl directpv init drives.yaml
kubectl directpv init drives.yaml --dangerous
kubectl directpv list drives
```

## Using MetalLB to provision External IP for LoadBalancer service on Kind Kubernetes cluster (Bare Metal)

MetalLB is a load-balancer implementation for bare metal Kubernetes clusters using standard routing protocols. This means that you can use MetalLB to expose services with external IPs in scenarios where you do not have cloud providers or load balancers that can provide this functionality natively.
MetalLB is a service for Kubernetes that provides load balancing to application services in the Kubernetes environment. It allows external traffic to reach services inside the Kubernetes cluster.

MetalLB operates by watching the Kubernetes API for services that request load balancing, then assigns an external IP address from a pool to those services. It does this by speaking standard routing protocols with your network infrastructure, such as BGP or ARP.

- How to install?

First if you are using kube-proxy in IPVS mode, it is necessary to enable ARP mode. To do this, you need edit the kube-proxy config in your cluster:

```bash
kubectl edit configmap -n kube-system kube-proxy
```

This will open the Vim editor. Using the arrow keys on the keyboard, scroll down through the text until you reach the line with the information `strictARP: false`. When you find it, move the cursor to the end of the word `false` using the arrow keys, press "x" to delete the word, then press "Esc". After that, press the letter "i" and type `true`. Press "Esc" again to exit insert mode, and type ":wq" to save and close the file.

Then install Metallb by Manifest:

```bash
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.14.3/config/manifests/metallb-native.yaml
```

- Config IP's pools

To config Ips pools correctly, it's important to know the ip ranges from our kind cluster.

```bash
docker network inspect kind
```

Search for some rows like this:

```bash
    "Config": [
                {
                    "Subnet": "172.1.0.0/16",
                    "Gateway": "172.1.0.1"
                },
```

Now, write a `.yaml` file with the IPAddressPool and  L2Advertisement resource. My file are in `infra/terraform/gitops/metallb/metallb_configips.yaml` directory. And apply with `kubectl`. This is enough to configure the load balancer.


## Creating ArgoCD Service

- Add helm repository to argocd

```bsh
helm repo add argo https://argoproj.github.io/argo-helm
```

- Build using Terraform

Create a `.tf` file with your requirements to the resource. My requirements are in `argocd.tf` file. Then, just execute the following commands:

```bsh
terraform init
terraform plan
terraform apply -auto-approve
```

- Manual configuration to your service:

This configs also can build using the helm repository. The first configuration we can do is access the service, Loadbalancer or Nodeport (configured by default). As we are using our on-premise cluster, operating the load balancer is just possible with Metallb. If we were in a cloud environment or using Metallb, we could do: `kubectl patch svc argocd-server -n gitops -p '{"spec": {"type": "LoadBalancer"}}'`.

To access the ArgoCD service We need to use our cluster id. Get your cluster id with:

```bsh
kubectl get nodes -o wide
```

Then access in your browse `http://<cluster_ip>:<nodePort>/`.

Configure a user and a password to login:

```sh

kubectl get svc argocd-server -n gitops
# get argocd password
kubectl -n gitops get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d; echo
```

- Install ArgoCD CLI and do your login:
  
```sh
brew install argocd
```


```sh
argocd login "<cluster_ip>" --username admin --password "xxxx" --insecure
argocd login "172.18.0.50" --username admin --password "lbPF8ocqQqjhK74d" --insecure
```

- Add cluster to ArgoCD

To add our cluster into ArgoCD, We need to change the cluster id in `.kube/config`. First get the endpoint of kubernetes cluster.

```sh
$ kubectl get endpoints
NAME         ENDPOINTS         AGE
kubernetes   <cluster_ip:port>  2d7h
```

Then replace this endpoint into `~/.kube/config`.

```sh
 cluster:
    certificate-authority-data: 0tLS1CRUdJTiBDRVJUS
    server: https://127.0.0.1:4624 #replace here
  name: kind-modern-stack
```

Now add your cluster with:

```sh
argocd cluster add kind-modern-stack
```

- Add Github Repo:

```sh
kubectl apply -f git-repo-con.yaml -n gitops
```

## Installation of Ingress Nginx

[Ingress Nginx](https://kubernetes.github.io/ingress-nginx/) is an Ingress controller for kubernetes using Nginx as a reverse proxy and load balancer. It is the most popular Ingress controller for kubernetes. He is reliable and easy to use, providing load balancing, SSL termination, and name-based virtual routing features. However, it does not support dynamic configurations, so an NGINX reload is required whenever a new Kubernetes endpoint is defined.The ingress controller is for pointing DNS names to our cluster and then routing them to the proper pods inside the cluster. So this is HTTP and HTTPS traffic only.

```bash
helm upgrade --install ingress-nginx ingress-nginx --version 4.9.1 --repo https://kubernetes.github.io/ingress-nginx --namespace ingress-nginx --create-namespace --set controller.replicaCount=1 --set controller.ingressClassResource.default=true

# Explore created resources
kubectl get ingressclass
kubectl get pods -A
kubectl get pods --namespace=ingress-nginx
```

Now We have to create the roles to point our DNS. 

- Ingress Rules: The administrator defines Ingress rules in YAML resources, which specify how external traffic should be routed to services within the cluster. The rules typically include information such as hosts and paths to be mapped to specific services.

- Ingress Controller: The NGINX Ingress Controller continuously monitors Ingress resources in Kubernetes to detect changes. When new Ingress rules are created, updated, or deleted, the Ingress Controller reacts to these changes and updates the NGINX configuration accordingly.

- NGINX Configuration: Based on the Ingress rules, the Ingress Controller generates and updates the NGINX configuration. This may include defining virtual hosts, redirection rules, load balancing, SSL termination, and other configurations necessary to route traffic correctly.

- Reverse Proxy: NGINX acts as a reverse proxy, receiving incoming requests from the external world and forwarding them to the appropriate services within the cluster based on the configured Ingress rules.

- Traffic Routing: Based on the hosts and paths defined in the Ingress rules, NGINX routes Internet traffic to the pods corresponding to the specified services.

Essentially, the NGINX Ingress Controller simplifies and automates the process of configuring NGINX to handle external traffic routing to services within the Kubernetes cluster, allowing developers and system administrators to easily define traffic routing rules declaratively using Ingress resources.

- How to Create a rule in my local machine?

```bash
sudo nano /etc/hosts 

  GNU nano 4.8                                                                                 /etc/hosts                                                                                 Modified  
127.0.0.1       localhost
127.0.1.1       wesley-ds

# Add by Kubernetes
# ips to nginx from modern-data-stack cluster pool
172.18.0.51     modern_data_stack.com.br          # add this line
```

The following steps are create the `.yaml` file to specify the pods with service.


## Install MinIo Storage Operator

MinIO is an open-source, distributed object storage software designed to be scalable, high-performance, and highly available. It is capable of storing and retrieving large volumes of unstructured data such as images, videos, documents, and other file types. MinIO implements the Amazon Web Services (AWS) S3 object storage protocol, making it compatible with many tools and applications that use this protocol.

```bash
kubectl apply -f app-manifests/deepstorage/minio-operator.yaml
```

## Install MinIo Tenant

MinIO Tenant is a more recent feature of MinIO that provides the ability to share a single MinIO cluster among multiple teams, departments, or clients. It offers data and resource isolation for each tenant, allowing different groups of users to share the same storage environment without compromising security or performance. MinIO Tenant simplifies data management in multi-tenant environments by providing efficient and scalable features for tenant creation, isolation, access control, and monitoring.

```bash
kubectl apply -f app-manifests/deepstorage/minio-tenant.yaml
```

## Install Hive Metastore

The Hive Metastore is a key component of Apache Hive, a data warehousing tool built on the Hadoop framework. The Hive Metastore serves as a centralized metadata repository that stores information about the data stored in the Hadoop Distributed File System (HDFS) or another Hadoop-compatible storage system. It maintains records of data schemas, physical file locations, table statistics, and other information necessary for executing SQL queries on this data.

In simple terms, the Hive Metastore functions as a metadata catalog for Hive, enabling users to query and analyze data stored in Hadoop similar to a relational database. It provides an abstraction layer between the physical data stored and the SQL queries executed by users, allowing users to focus on query logic rather than dealing directly with data storage and location details.

Additionally, the Hive Metastore supports advanced features such as table partitioning, dynamic schema management, and data access control, making it a crucial component in big data infrastructure for data analysis at scale.

Regarding how to use Hive Metastore with MinIO, MinIO itself doesn't directly integrate with Hive Metastore out of the box. However, MinIO can serve as a storage backend for Hadoop-based solutions like Hive. You can configure Hive to use MinIO as its storage layer by setting up MinIO as an external storage system accessible via its S3-compatible API. Then, you can configure Hive to store its data on MinIO by specifying the appropriate endpoint, access credentials, and bucket details in the Hive configuration. This setup allows you to leverage the scalability and performance of MinIO storage while benefiting from the data processing capabilities of Hive.

```shell
kubectl apply -f app-manifests/metastore/hive-metastore.yaml
```

## Install Trino

Trino is an open-source distributed SQL query engine designed for fast and interactive analytics on large-scale datasets. It was originally developed by Facebook and later open-sourced. Trino allows users to run ad-hoc SQL queries across multiple data sources, such as Hadoop Distributed File System (HDFS), Apache Cassandra, relational databases, and many others, without needing to move or transform the data.

Key features of Trino include:

1. **Distributed Query Processing**: Trino employs a distributed architecture where queries are broken down into smaller tasks that are executed in parallel across a cluster of machines. This enables Trino to scale horizontally and process queries efficiently on large datasets.

2. **High Performance**: Trino is optimized for speed and can handle complex queries on petabytes of data with low latency. It achieves this by utilizing in-memory processing, efficient query planning, and advanced optimization techniques.

3. **Connectivity to Various Data Sources**: Trino supports a wide range of data sources and formats, including traditional relational databases (such as MySQL, PostgreSQL, and SQL Server), NoSQL databases (such as Cassandra and MongoDB), cloud storage (like Amazon S3 and Google Cloud Storage), and more. This allows users to query data across diverse data sources using a unified SQL interface.

4. **SQL Compatibility**: Trino supports standard SQL syntax, allowing users to write queries using familiar SQL constructs. It also offers support for advanced SQL features like joins, subqueries, window functions, and aggregations.

5. **Dynamic Scaling**: Trino can dynamically allocate and release computing resources based on query demands, ensuring optimal resource utilization and performance.

6. **Security**: Trino provides robust security features, including authentication, authorization, encryption, and auditing, to ensure the confidentiality and integrity of data.

Overall, Trino is a powerful tool for data analysts, engineers, and scientists who need to perform fast and interactive analytics across a variety of data sources, enabling them to derive valuable insights from their data quickly and efficiently.

```shell
kubectl apply -f app-manifests/warehouse/trino.yaml
```