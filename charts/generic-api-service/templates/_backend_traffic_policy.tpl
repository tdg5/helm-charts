{{- define "generic-api-service.backend-traffic-policy" -}}
{{- $globalScope := index . 0 -}}
{{- $policyScope := index . 1 -}}

{{- if $policyScope.create -}}
{{- $apiVersion := include "generic-api-service.backend-traffic-policy-api-version" $globalScope -}}
{{-
  $targetRefs := $policyScope.targetRefs |
    default nil |
    required "A valid .targetRefs mapping is required."
-}}
{{- $fullName := include "generic-api-service.full-name" $globalScope -}}
apiVersion: {{ $apiVersion }}
kind: BackendTrafficPolicy
metadata:
  {{- with $policyScope.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
  labels:
    {{- include "generic-api-service.labels" $globalScope | nindent 4 }}
  name: {{ $policyScope.name | default $fullName }}
spec:
  targetRefs:
  {{- range $targetRefs }}
  - group: {{ .group | default "gateway.networking.k8s.io" | quote }}
    kind: {{ .kind | default "HTTPRoute" }}
    name: {{ .name | default $fullName }}
    {{- with .sectionName }}
    sectionName: {{ . }}
    {{- end }}
  {{- end }}
  {{- with omit ($policyScope.spec | default dict) "targetRefs" }}
  {{- toYaml . | nindent 2 }}
  {{- end }}
{{- end }}
{{- end -}}
