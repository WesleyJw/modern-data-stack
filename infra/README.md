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
kind create cluster --name modern-stack --kind.yaml
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

## Creating ArgoCD Service

- Add helm repository to argocd

```bsh
helm repo add argo https://argoproj.github.io/argo-helm
```

- Build using Terraform

```bsh
terraform init
terraform plan
terraform apply -auto-approve
```

- Manual configuration to your service:

This configs also can build using the helm repository. The first configuration we can do is access the service, Loadbalancer or Nodeport (configured by default). As we are using our on-premise cluster, operating the load balancer is impossible. If we were in a cloud environment, we could do: `kubectl patch svc argocd-server -n gitops -p '{"spec": {"type": "LoadBalancer"}}'`.

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
```

- Add cluster to ArgoCD

To add our cluster into ArgoCD, We need to change the cluster id in `.kube/config`. First get the endpoint of kubernetes cluster.

```sh
$ kubectl get endpoints
NAME         ENDPOINTS         AGE
kubernetes   <cluster_ip:port>  2d7h
```

Then replace this endpoint into `.kube/config`.

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

