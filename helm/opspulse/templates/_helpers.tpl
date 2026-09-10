{{- define "opspulse.name" -}}
opspulse
{{- end -}}

{{- define "opspulse.fullname" -}}
{{- printf "%s-%s" .Release.Name (include "opspulse.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "opspulse.labels" -}}
app.kubernetes.io/name: {{ include "opspulse.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{- define "opspulse.selectorLabels" -}}
app.kubernetes.io/name: {{ include "opspulse.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "opspulse.serviceAccountName" -}}
{{- if .Values.serviceAccount.create -}}
{{- default (include "opspulse.fullname" .) .Values.serviceAccount.name -}}
{{- else -}}
{{- default "default" .Values.serviceAccount.name -}}
{{- end -}}
{{- end -}}
