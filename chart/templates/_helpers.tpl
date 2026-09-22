{{/*
Common label block applied to every resource this chart renders.
*/}}
{{- define "k8sbase.labels" -}}
app.kubernetes.io/part-of: {{ .Values.project.name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{/*
Stable per-pod DNS name for the mongodb-0 replica (headless service).
*/}}
{{- define "mongodb.dns" -}}
{{ .Values.mongodb.name }}-0.{{ .Values.mongodb.name }}.{{ .Values.namespaces.db }}.svc.cluster.local
{{- end -}}

{{/*
Full Mongo connection string used by the backend.
*/}}
{{- define "mongodb.uri" -}}
mongodb://{{ .Values.mongodb.auth.rootUsername }}:{{ .Values.mongodb.auth.rootPassword }}@{{ include "mongodb.dns" . }}:{{ .Values.mongodb.port }}/{{ .Values.mongodb.auth.database }}?authSource=admin
{{- end -}}
