# openvpn-as

## Credit

This helm chart is based on
[stenic/helm-charts](https://github.com/stenic/helm-charts/tree/master/charts/openvpn-as).
It was forked out of an abundance of caution motivated by baseless paranoia.

## TL;DR

```bash
helm repo add tdg5 https://tdg5.github.io/helm-charts/
helm install my-release --set "service.type=LoadBalancer" tdg5/openvpn-as
```

## Introduction

This chart installs `openvpn-as` on a [Kubernetes](http://kubernetes.io) cluster using the [Helm](https://helm.sh) package manager.

[![openvpn-as](https://raw.githubusercontent.com/tdg5/helm-charts/main/charts/openvpn-as/openvpn-as.png)](https://openvpn.net/index.php/access-server/overview.html)

## Prerequisites

- Kubernetes 1.12+
- Helm 3.0+
- LoadBalancer to expose the vpn service
- PV provisioner support in the underlying infrastructure

## Installing the Chart

To install the chart with the release name `my-release`:

```bash
helm repo add tdg5 https://tdg5.github.io/helm-charts/
helm install my-release --set "service.type=LoadBalancer" tdg5/openvpn-as
```

These commands deploy openvpn-as on the Kubernetes cluster in the default configuration. The [Parameters](#parameters) section lists the parameters that can be configured during installation.

> **Tip**: List all releases using `helm list`

## Uninstalling the Chart

To uninstall/delete the `my-release` deployment:

```bash
helm delete my-release
```

The command removes all the Kubernetes components associated with the chart and deletes the release.

## Configuration

The following tables list the configurable parameters of the openvpn-as chart and their default values.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| affinity | object | `{}` | Affinity labels for pod assignment |
| fullnameOverride | string | `""` |  |
| image.pullPolicy | string | `"IfNotPresent"` | Image pull policy |
| image.repository | string | `"openvpn/openvpn-as"` | Image repository |
| image.tag | string | `""` | Image tag |
| imagePullSecrets | list | `[]` | Registry secret names as an array |
| ingress.admin.annotations | object | `{}` | Ingress annotations |
| ingress.admin.enabled | bool | `false` | Enable ingress resource for Admin UI |
| ingress.admin.hostName | string | `"admin.openvpn.local"` | Host for the Admin UI |
| ingress.admin.ingressClassName | string | `nil` | set ingressClassName here, or leave it unset |
| ingress.admin.tls.enabled | bool | `true` | Enable TLS configuration for the hostname defined at ingress.admin.hostname parameter |
| ingress.admin.tls.secretName | string | `"admin.openvpn-tls"` |  |
| ingress.ui.annotations | object | `{}` | Ingress annotations |
| ingress.ui.enabled | bool | `false` | Enable ingress resource for Client UI |
| ingress.ui.hostName | string | `"client.openvpn.local"` | Host for the Client UI |
| ingress.ui.ingressClassName | string | `nil` | Set ingressClassName here, or leave it unset |
| ingress.ui.tls.enabled | bool | `true` | Enable TLS configuration for the hostname defined at ingress.ui.hostname parameter |
| ingress.ui.tls.secretName | string | `"client.openvpn-tls"` |  |
| nameOverride | string | `""` |  |
| nodeSelector | object | `{}` | Node labels for pod assignment |
| openvpn.admin.password | string | `"passw0rd"` | Password for the initial super_user |
| openvpn.admin.user | string | `"altmin"` | Username for the initial super_user. Cannot be `admin` |
| openvpn.config | object | `{"vpn.client.routing.reroute_dns":"false","vpn.client.routing.reroute_gw":"false"}` | Config settings to apply to the openvpn-as server |
| openvpn.ports.admin | int | `943` | Admin UI port |
| openvpn.ports.tcp | int | `9443` | VPN TCP port |
| openvpn.ports.udp | int | `1194` | VPN UDP port |
| openvpn.ports.ui | int | `944` | Client UI port |
| openvpn.timezone | string | `"Etc/UTC"` |  |
| openvpn.users | list | `nil` | Additional users to create when non-existent `[{"user":"someuser","password":"somepassword"}]` |
| persistence.accessMode | string | `"ReadWriteOnce"` | PVC Access Mode for volume |
| persistence.annotations | object | `{}` | Annotations for the PVC |
| persistence.backupSubpath | string | `"backup"` | Indicate another subpath for backup storage |
| persistence.enabled | bool | `true` | Enable persistence using PVC |
| persistence.existingClaimName | string | `nil` | used when PVC already created before install |
| persistence.licensesSubpath | string | `"licenses"` | Indicate another subpath for licenses storage |
| persistence.size | string | `"8Gi"` | PVC Storage Request for volume |
| persistence.storageClass | string | `nil` | PVC Storage Class for volume |
| podAnnotations | object | `{}` | Map of annotations to add to the pods |
| podSecurityContext.fsGroup | int | `1000` | Group ID for the pod |
| replicaCount | int | `1` |  |
| resources | object | `{}` | CPU/Memory resource requests/limits |
| securityContext | object | `{"capabilities":{"add":["NET_ADMIN"]}}` | Security Context |
| service.admin.type | string | `"ClusterIP"` | Kubernetes Service type for Admin UI |
| service.tcp.enabled | bool | `true` |  |
| service.type | string | `"ClusterIP"` | Kubernetes Service type for VPN, generally this is "LoadBalancer" |
| service.udp.enabled | bool | `true` |  |
| service.ui.type | string | `"ClusterIP"` | Kubernetes Service type for Client UI |
| serviceAccount.annotations | object | `{}` |  |
| serviceAccount.create | bool | `true` | Create ServiceAccount |
| serviceAccount.name | string | `""` |  |
| tolerations | list | `[]` | Toleration labels for pod assignment |

Specify each parameter using the `--set key=value[,key=value]` argument to `helm install`.

Alternatively, a YAML file that specifies the values for the parameters can be provided while installing the chart. For example,

```bash
helm install my-release -f values.yaml tdg5/openvpn-as
```
