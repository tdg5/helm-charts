{{- define "generic-api-service.http-route" -}}
{{- $globalScope := index . 0 -}}
{{- $routeScope := index . 1 -}}

{{- if $routeScope.create -}}
{{- $httpRouteApiVersion := include "generic-api-service.http-route-api-version" $globalScope -}}
{{-
  $parentRefs := $routeScope.parentRefs |
    default nil |
    required "A valid .parentRefs mapping is required."
-}}
{{- $serviceName := include "generic-api-service.service-name" $globalScope -}}
apiVersion: {{ $httpRouteApiVersion }}
kind: HTTPRoute
metadata:
  {{- with $routeScope.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
  labels:
    {{- include "generic-api-service.labels" $globalScope | nindent 4 }}
  name: {{ $routeScope.name | default (include "generic-api-service.full-name" $globalScope) }}
spec:
  parentRefs:
  {{- range $parentRefs }}
  - group: {{ .group | default "gateway.networking.k8s.io" }}
    kind: {{ .kind | default "Gateway" }}
    name: {{ required "A valid .name is required for each parentRef." .name }}
    {{- with .namespace }}
    namespace: {{ . }}
    {{- end }}
    {{- with .sectionName }}
    sectionName: {{ . }}
    {{- end }}
    {{- with .port }}
    port: {{ . }}
    {{- end }}
  {{- end }}
  {{- with $routeScope.hostnames }}
  hostnames:
  {{- range . }}
  - {{ . | quote }}
  {{- end }}
  {{- end }}
  {{- if $routeScope.rules }}
  rules:
  {{- range $routeScope.rules }}
  -
    {{- if .backendRefs }}
    backendRefs:
    {{- range .backendRefs }}
    - group: {{ .group | default "" | quote }}
      kind: {{ .kind | default "Service" }}
      name: {{ .name | default $serviceName }}
      port: {{ include "generic-api-service.service-port-number" (list $globalScope .portName) }}
      weight: {{ if hasKey . "weight" }}{{ .weight }}{{ else }}1{{ end }}
    {{- end }}
    {{- end }}
    {{- with .matches }}
    matches:
    {{- range . }}
    - path:
        type: {{ .path.type }}
        value: {{ .path.value }}
      {{- with .method }}
      method: {{ . }}
      {{- end }}
    {{- end }}
    {{- end }}
  {{- end }}
  {{- end }}
{{- end }}
{{- end -}}
