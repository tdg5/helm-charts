# generic-api-service

## Introduction

This chart is a one-size-fits-many approach for deploying API service
applications to a [Kubernetes](http://kubernetes.io) cluster using the
[Helm](https://helm.sh) package manager.

It acts as an interface/adapter so that a typical API deployment can be
expressed primarily in YAML, with limited knowledge of the underlying
Kubernetes resources. Traffic is routed exclusively via
[Gateway API](https://gateway-api.sigs.k8s.io/) resources (HTTPRoute,
BackendTLSPolicy) and [Envoy Gateway](https://gateway.envoyproxy.io/)
BackendTrafficPolicy resources; Ingress is not supported.

## Prerequisites

- Kubernetes 1.28+
- Helm 3.0+
- The [Gateway API](https://gateway-api.sigs.k8s.io/) CRDs and a compatible
  Gateway controller (e.g. [Envoy Gateway](https://gateway.envoyproxy.io/)),
  required when using the `httpRoutes`, `backendTrafficPolicies`, or
  `backendTLSPolicies` values.

## Installing the Chart

Unlike some other Helm charts that come with a deployable default
configuration, this Helm chart requires customized values in order to be
deployable.

See the [Configuration](#configuration) section for more information on
customizing/configuring your installation.

## Configuration

The following table enumerates the configurable parameters of the
generic-api-service chart and any default values that are defined.

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| appName | string | `""` | The name of the application or service being deployed. |
| appVersion | string | `""` | The version of the application or service being deployed. When not provided, container.image.tag will be used instead. |
| backendTLSPolicies | object | -- | An optional map where each key is an arbitrary identifier (to facilitate overriding) and each value is an object of Gateway API BackendTLSPolicy configuration. Re-encrypts Gateway-to-backend traffic over TLS (the Gateway API analog of the nginx Ingress backend-protocol: HTTPS annotation). |
| backendTrafficPolicies | object | -- | An optional map where each key is an arbitrary identifier (to facilitate overriding) and each value is an object of Envoy Gateway BackendTrafficPolicy configuration. Applies traffic settings (e.g. request timeouts) to routes or services (the Gateway API analog of nginx proxy-read-timeout and friends). |
| container | object | -- | Various configuration related to the deployed container. |
| container.env | object | `{}` | An optional mapping where each key is an arbitrary identifier (to facilitate overriding) and each value is an EnvVar spec. |
| container.image | object | -- | Various configuration related to the container image. |
| container.image.pullPolicy | string | `"IfNotPresent"` | The pull policy to use for the image. |
| container.image.repository | string | `""` | The repository containing the image that should be deployed. |
| container.image.tag | string | `""` | The image tag that should be used by the deployment. |
| container.livenessProbe | object | -- | Liveness probe configuration for the container. |
| container.livenessProbe.httpGet | object | -- | A string key that identifies the type of liveness probe and a mapping describing the liveness probe. |
| container.livenessProbe.httpGet.path | string | `"/livez"` | The path that should be accessed when using an HTTP GET liveness probe. |
| container.livenessProbe.httpGet.port | string | `"http"` | The name of the port that should be accessed when using an HTTP GET liveness probe. |
| container.readinessProbe | object | -- | Readiness probe configuration for the container. |
| container.readinessProbe.httpGet | object | -- | A string key that identifies the type of readiness probe and a mapping describing the readiness probe. |
| container.readinessProbe.httpGet.path | string | `"/readyz"` | The path that should be accessed when using an HTTP GET readiness probe. |
| container.readinessProbe.httpGet.port | string | `"http"` | The name of the port that should be accessed when using an HTTP GET readiness probe. |
| container.resources | object | `{}` | The resources that the container requests and is limited to. |
| container.securityContext | object | `{}` | The security context that should be applied to the container. |
| container.startupProbe | object | -- | Startup probe configuration for the container. |
| container.volumeMounts | object | `{}` | Pod volumes to mount into the container's filesystem given in the form of an object where each key is an arbitrary identifier (to facilitate overridding) and each value is an object of volume mount configuration. |
| fullNameOverride | string | `""` | Value to use for generating full object names instead of the standard template based logic. |
| httpRoutes | object | -- | An optional map where each key is an arbitrary identifier (to facilitate overriding) and each value is an object of Gateway API HTTPRoute configuration. HTTPRoutes are the Gateway API mechanism for routing traffic from a Gateway to this chart's service. |
| namespace | object | -- | Various configuration related to the namespace that resources should be deployed to. |
| namespace.create | bool | `false` | Flag indicating whether or not a namespace resource should be created. |
| namespace.name | string | `""` | The name that should be given to the namespace and used as a namespace for other resources. When omitted, resources are not assigned an explicit namespace. |
| persistentVolumeClaims | object | -- | An optional map where each key is an arbitrary identifier (to facilitate overriding) and each value is an object of PersistentVolumeClaim configuration. Use for stateful workloads that need a persistent volume; mount the resulting claim via pod.volumes + container.volumeMounts. |
| pod | object | -- | Various configuration for the application deployment pod. |
| pod.affinity | object | `{}` | Affinity rules that should be applied to the pod to customize scheduling. |
| pod.annotations | object | `{}` | Annotations that should be added to the pod. |
| pod.imagePullSecrets | object | `{}` | An optional mapping where each key is an arbitrary identifier (to faciliate overriding) and each value is a reference to a secret in the same namespace to use for pulling any of the images used by the PodSpec. |
| pod.labels | object | `{}` | Labels that should be added to the pod. |
| pod.nodeSelector | object | `{}` | An optional selector which must be true for the pod to fit on a node. |
| pod.securityContext | object | `{}` | The security context that should be applied to the pod. |
| pod.tolerations | object | `{}` | An optional mapping where each key is an arbitrary identifier (to facilitate overriding) and each value is an object describing criteria for matching taints that the pod should tolerate. |
| pod.volumes | object | `{}` | An optional mapping where each key is an arbitrary identifier (to facilitate overriding) and each value is an object describing a volume that can be mounted by containers belonging to the pod. |
| ports | object | -- | A list of onfigurations for the ports that the container/service should expose. |
| ports.http | object | -- | An arbitrary alias for the port to facilitate overriding. |
| ports.http.containerPort | int | `80` | The port that the container should publish. |
| ports.http.name | string | `"http"` | The name that should be used to reference the container port and service port. |
| ports.http.protocol | string | `"TCP"` | The protocol that is handled by the port. |
| ports.http.servicePort | int | `80` | The port that the service should publish. |
| replicaCount | int | `1` | The number of pod replicas that should be run by the deployment. |
| revisionHistoryLimit | int | `5` | The number of historical deployment revisions to retain. |
| service | object | -- | Various configuration for the service object. |
| service.create | bool | `true` | Flag indicating whether or not a service resource should be created. |
| service.name | string | `""` | The name that should be given to the service. |
| service.type | string | `"ClusterIP"` | Determines how the service is exposed. |
| serviceAccount | object | -- | Various configuration for the service account object. |
| serviceAccount.annotations | object | `{}` | A mapping of arbitrary metadata to associate with the service account. |
| serviceAccount.automount | bool | `true` | Flag that indicates whether pods running as this service account should have an API token automatically mounted. |
| serviceAccount.create | bool | `true` | Flag indicating whether or not a service account object should be created. |
| serviceAccount.labels | object | `{}` | A mapping of arbitrary labels to apply to the service account. |
| serviceAccount.name | string | `""` | Name that should be given to the service account.  If not set and create is true, a name is genered from the full-name template. |
| strategy | object | -- | The deployment update strategy, passed through verbatim (e.g. a RollingUpdate config, or {type: Recreate}). Omitted when empty, leaving the Kubernetes default (RollingUpdate). |

A YAML file that specifies the values for the parameters should be provided
while installing the chart.

Alternatively, each parameter can be specified using a `--set key=value`
argument to `helm install`.
