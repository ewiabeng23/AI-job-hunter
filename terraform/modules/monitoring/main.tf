# Add Helm repos
resource "helm_release" "prometheus" {
  name             = "prometheus"
  repository       = "https://prometheus-community.github.io/helm-charts"
  chart            = "kube-prometheus-stack"
  namespace        = "monitoring"
  create_namespace = true
  version          = "45.7.1"

  set {
    name  = "grafana.adminPassword"
    value = var.grafana_password
  }

  set {
    name  = "prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues"
    value = "false"
  }

  set {
    name  = "grafana.service.type"
    value = "NodePort"
  }

  set {
    name  = "grafana.service.nodePort"
    value = "32001"
  }

  depends_on = [var.eks_cluster_name]
}

# ELK Stack
resource "helm_release" "elasticsearch" {
  name             = "elasticsearch"
  repository       = "https://helm.elastic.co"
  chart            = "elasticsearch"
  namespace        = "logging"
  create_namespace = true
  version          = "8.5.1"

  set {
    name  = "replicas"
    value = "1"
  }

  set {
    name  = "minimumMasterNodes"
    value = "1"
  }

  set {
    name  = "resources.requests.memory"
    value = "512Mi"
  }

  set {
    name  = "resources.limits.memory"
    value = "1Gi"
  }

  depends_on = [var.eks_cluster_name]
}

resource "helm_release" "kibana" {
  name       = "kibana"
  repository = "https://helm.elastic.co"
  chart      = "kibana"
  namespace  = "logging"
  version    = "8.5.1"

  set {
    name  = "service.type"
    value = "NodePort"
  }

  set {
    name  = "service.nodePort"
    value = "32002"
  }

  depends_on = [helm_release.elasticsearch]
}

resource "helm_release" "logstash" {
  name       = "logstash"
  repository = "https://helm.elastic.co"
  chart      = "logstash"
  namespace  = "logging"
  version    = "8.5.1"

  depends_on = [helm_release.elasticsearch]
}

resource "helm_release" "filebeat" {
  name       = "filebeat"
  repository = "https://helm.elastic.co"
  chart      = "filebeat"
  namespace  = "logging"
  version    = "8.5.1"

  depends_on = [helm_release.elasticsearch]
}
