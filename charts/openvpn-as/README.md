# openvpn-as

## Quick Install

```bash
helm repo add tdg5 https://tdg5.github.io/helm-charts/
helm install openvpn-as-release --set "service.type=LoadBalancer" tdg5/openvpn-as
```

## Introduction

This chart installs `openvpn-as` on a
[Kubernetes](http://kubernetes.io) cluster using the [Helm](https://helm.sh)
package manager.

[![openvpn-as](https://raw.githubusercontent.com/tdg5/helm-charts/main/charts/openvpn-as/openvpn-as.png)](https://openvpn.net/index.php/access-server/overview.html)

## Prerequisites

- Kubernetes 1.22+
- Helm 3.0+
- Support for LoadBalancer resources to expose openvpn-as
  services
- Support for PersistentVolumes for persistent openvpn-as
  data

## Installing the Chart

To install the chart with the default configuration and the release name
`openvpn-as-release`:

```bash
helm repo add tdg5 https://tdg5.github.io/helm-charts/
helm install openvpn-as-release --set "service.type=LoadBalancer" tdg5/openvpn-as
```

See the [Configuration](#configuration) section for more information on
customizing/configuring your installation.

## Uninstalling the Chart

To remove all the Kubernetes components associated with the
`openvpn-as` chart and delete the release, run the following
command:

```bash
helm delete openvpn-as-release
```

## Configuration

The following table enumerates the configurable parameters of the
openvpn-as chart and any default values that are defined.

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| affinity | object | `{}` | Affinity labels for pod assignment |
| fullnameOverride | string | `""` |  |
| image.pullPolicy | string | `"IfNotPresent"` | Image pull policy |
| image.repository | string | `"openvpn/openvpn-as"` | Image repository |
| image.tag | string | `""` | Image tag |
| imagePullSecrets | list | `[]` | Registry secret names as an array |
| ingress | object | `{"annotations":{},"enabled":false,"hostName":"client.openvpn.local","ingressClassName":null,"tls":{"enabled":true,"secretName":"client.openvpn-tls"}}` | Ingress configuration |
| ingress.annotations | object | `{}` | Ingress annotations |
| ingress.enabled | bool | `false` | Enable ingress resource for Client UI |
| ingress.hostName | string | `"client.openvpn.local"` | Host for the ingress |
| ingress.ingressClassName | string | `nil` | Set ingressClassName here, or leave it unset |
| ingress.tls.enabled | bool | `true` | Enable TLS configuration for the hostname defined at ingress.hostName parameter |
| nameOverride | string | `""` |  |
| nodeSelector | object | `{}` | Node labels for pod assignment |
| persistence.accessMode | string | `"ReadWriteOnce"` | PVC Access Mode for volume |
| persistence.annotations | object | `{}` | Annotations for the PVC |
| persistence.enabled | bool | `true` | Enable persistence using PVC |
| persistence.existingClaimName | string | `nil` | used when PVC already created before install |
| persistence.licensesSubpath | string | `"licenses"` | Indicate another subpath for licenses storage |
| persistence.size | string | `"8Gi"` | PVC Storage Request for volume |
| persistence.storageClass | string | `nil` | PVC Storage Class for volume |
| podAnnotations | object | `{}` | Map of annotations to add to the pods |
| podSecurityContext | string | `nil` | Map of pod security context values |
| replicaCount | int | `1` |  |
| resources | object | `{}` | CPU/Memory resource requests/limits |
| securityContext | object | `{"capabilities":{"add":["NET_ADMIN"]}}` | Security Context |
| service.type | string | `"ClusterIP"` | Kubernetes Service type for Client UI |
| service.vpnTcpPort | int | `443` | VPN TCP port |
| service.vpnUdpPort | int | `1194` | VPN UDP port |
| service.vpnUiPort | int | `943` | Client UI port |
| serviceAccount.annotations | object | `{}` | Annotations for the service account. |
| serviceAccount.create | bool | `true` | Create ServiceAccount |
| serviceAccount.name | string | `""` | Name to give the service account. |
| timezone | string | `"Etc/UTC"` | The timezone that should be used. |
| tolerations | list | `[]` | Tolerations for for the pod. |

A YAML file that specifies the values for the parameters can be provided while
installing the chart like so:

```bash
helm install openvpn-as-release -f values.yaml tdg5/openvpn-as
```

Alternatively, each parameter can be specified using a `--set
key=value` argument to `helm install`.

## Credit

This helm chart is originally based on
[stenic/helm-charts](https://github.com/stenic/helm-charts/tree/master/charts/openvpn-as).
