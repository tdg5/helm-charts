{{- define "generic-api-service.persistent-volume-claim" -}}
{{- $globalScope := index . 0 -}}
{{- $id := index . 1 -}}
{{- $pvcScope := index . 2 -}}

{{- if $pvcScope.create -}}
{{- $fullName := include "generic-api-service.full-name" $globalScope -}}
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  {{- with $pvcScope.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
  labels:
    {{- include "generic-api-service.labels" $globalScope | nindent 4 }}
  name: {{ $pvcScope.name | default (printf "%s-%s" $fullName $id) }}
spec:
  {{- $pvcScope.spec | default dict | toYaml | nindent 2 }}
{{- end }}
{{- end -}}
