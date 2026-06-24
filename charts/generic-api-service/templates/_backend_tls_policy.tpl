{{- define "generic-api-service.backend-tls-policy" -}}
{{- $globalScope := index . 0 -}}
{{- $policyScope := index . 1 -}}

{{- if $policyScope.create -}}
{{- $apiVersion := include "generic-api-service.backend-tls-policy-api-version" $globalScope -}}
{{-
  $targetRefs := $policyScope.targetRefs |
    default nil |
    required "A valid .targetRefs mapping is required."
-}}
{{- $serviceName := include "generic-api-service.service-name" $globalScope -}}
apiVersion: {{ $apiVersion }}
kind: BackendTLSPolicy
metadata:
  {{- with $policyScope.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
  labels:
    {{- include "generic-api-service.labels" $globalScope | nindent 4 }}
  name: {{ $policyScope.name | default (include "generic-api-service.full-name" $globalScope) }}
spec:
  targetRefs:
  {{- range $targetRefs }}
  - group: {{ .group | default "" | quote }}
    kind: {{ .kind | default "Service" }}
    name: {{ .name | default $serviceName }}
    {{- with .sectionName }}
    sectionName: {{ . }}
    {{- end }}
  {{- end }}
  {{- with $policyScope.validation }}
  validation:
    {{- toYaml . | nindent 4 }}
  {{- end }}
{{- end }}
{{- end -}}
