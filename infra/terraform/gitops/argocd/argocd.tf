resource "helm_release" "argocd" {
  name             = "argocd"
  repository       = "https://argoproj.github.io/argo-helm/"
  chart            = "argo-cd"
  namespace        = "gitops"
  create_namespace = true
  version          = "5.38.0"
  verify           = false
  values           = [file("config.yaml")]
}
