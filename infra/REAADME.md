# Infra

## How to create a kind cluster

To create a cluster with `kind` We need to write a `.yaml` file with cluster specifications. Save the following steps in a file named  `kind.yaml`.

```shell
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
  - role: worker
  - role: worker
```

To create a cluster use:

```shell
kind create cluster --name modern-stack --kind.yaml
```

You can now check your cluster with:

```shell
kubectl cluster-info --context kind-modern-stack
```

Using `docker ps` you can see the created containers:

 ```shell
CONTAINER ID   IMAGE                  COMMAND                  CREATED       STATUS       PORTS                       NAMES
cd534bf47d15   kindest/node:v1.27.3   "/usr/local/bin/entr…"   3 hours ago   Up 3 hours   127.0.0.1:46247->6443/tcp   modern-stack-control-plane
9d7e05f4589a   kindest/node:v1.27.3   "/usr/local/bin/entr…"   3 hours ago   Up 3 hours                               modern-stack-worker
20b2c317ebe2   kindest/node:v1.27.3   "/usr/local/bin/entr…"   3 hours ago   Up 3 hours                               modern-stack-worker2
```

To set kubectl context to "kind-modern-stack" use this:

```shell

```

```shell

```