from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from prometheus_client import  Summary, Counter, Gauge
from flask import Response



REQUEST_COUNT = Counter('flask_app_requests_total', 'Total number of requests')
JOB_STATUS = Gauge('job_status', 'Whether the job is running (1) or stopped (0)')
JOB_DURATION = Summary('job_duration_seconds', 'Time spent processing job')


def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
