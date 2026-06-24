{{/*
Sanitize the name of the application.
*/}}
{{- define "generic-api-service.app-name" -}}
{{- .Values.appName | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create version of the application.
*/}}
{{- define "generic-api-service.app-version" -}}
{{- default .Values.container.image.tag .Values.appVersion }}
{{- end }}

{{/*
Create a default fully qualified name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "generic-api-service.full-name" -}}
{{- if .Values.fullNameOverride }}
{{- .Values.fullNameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := .Values.appName }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "generic-api-service.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels.
*/}}
{{- define "generic-api-service.labels" -}}
helm.sh/chart: {{ include "generic-api-service.chart" . }}
{{ include "generic-api-service.selector-labels" . }}
app.kubernetes.io/version: {{ include "generic-api-service.app-version" . | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels.
*/}}
{{- define "generic-api-service.selector-labels" -}}
app.kubernetes.io/name: {{ include "generic-api-service.app-name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use.
*/}}
{{- define "generic-api-service.service-account-name" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "generic-api-service.full-name" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Retrieve the namespace name that should be used.
*/}}
{{- define "generic-api-service.namespace-name" -}}
{{-
  .Values |
    merge (dict) |
    dig "namespace" "name" nil |
    default (include "generic-api-service.full-name" .)
-}}
{{- end -}}

{{/*
Retrieve the name that should be used for the service.
*/}}
{{- define "generic-api-service.service-name" -}}
{{-
  .Values |
    merge (dict) |
    dig "service" "name" nil |
    default (include "generic-api-service.full-name" .) |
    required "A valid .Values.service.name is required"
-}}
{{- end -}}

{{/*
Resolve the apiVersion that should be used for Gateway API HTTPRoute resources.
*/}}
{{- define "generic-api-service.http-route-api-version" -}}
{{- $apiVersion := "gateway.networking.k8s.io/v1" -}}
{{- $globalApiVersion := dig "global" "gatewayApi" "apiVersion" nil (.Values | merge (dict)) -}}
{{- if ne $globalApiVersion nil -}}
{{- $apiVersion = $globalApiVersion -}}
{{- end }}
{{- print $apiVersion -}}
{{- end -}}

{{/*
Resolve a service port number from a port name by looking it up in
.Values.ports. Accepts a list of [$globalScope, $portName].
*/}}
{{- define "generic-api-service.service-port-number" -}}
{{- $globalScope := index . 0 -}}
{{- $portName := index . 1 | required "A valid port name is required to resolve a service port number." -}}
{{- $servicePort := "" -}}
{{- range $globalScope.Values.ports -}}
{{- if eq .name $portName -}}
{{- $servicePort = .servicePort -}}
{{- end -}}
{{- end -}}
{{- if eq ($servicePort | toString) "" -}}
{{- fail (printf "Could not resolve a service port for port name %q." $portName) -}}
{{- end -}}
{{- $servicePort -}}
{{- end -}}

{{/*
Resolve the apiVersion that should be used for Gateway API BackendTLSPolicy
resources.
*/}}
{{- define "generic-api-service.backend-tls-policy-api-version" -}}
{{- $apiVersion := "gateway.networking.k8s.io/v1alpha3" -}}
{{- $globalApiVersion := dig "global" "gatewayApi" "backendTlsPolicyApiVersion" nil (.Values | merge (dict)) -}}
{{- if ne $globalApiVersion nil -}}
{{- $apiVersion = $globalApiVersion -}}
{{- end }}
{{- print $apiVersion -}}
{{- end -}}

{{/*
Resolve the apiVersion that should be used for Envoy Gateway
BackendTrafficPolicy resources.
*/}}
{{- define "generic-api-service.backend-traffic-policy-api-version" -}}
{{- $apiVersion := "gateway.envoyproxy.io/v1alpha1" -}}
{{- $globalApiVersion := dig "global" "gatewayApi" "backendTrafficPolicyApiVersion" nil (.Values | merge (dict)) -}}
{{- if ne $globalApiVersion nil -}}
{{- $apiVersion = $globalApiVersion -}}
{{- end }}
{{- print $apiVersion -}}
{{- end -}}
