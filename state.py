from threading import Lock
from uuid import uuid4

_jobs = {}
_lock = Lock()

def create_job(payload):
    job_id = str(uuid4())
    with _lock:
        _jobs[job_id] = {
            "id": job_id, "status": "queued", "progress": 0,
            "stage": "Waiting to start", "message": "Your production is queued",
            "logs": ["Production job created"], "completed_scenes": 0,
            "total_scenes": payload.scenes, "video_url": None, "error": None,
        }
    return job_id

def update_job(job_id, **fields):
    with _lock:
        if job_id in _jobs:
            _jobs[job_id].update(fields)

def log_job(job_id, message):
    with _lock:
        if job_id in _jobs:
            _jobs[job_id]["logs"].append(message)

def get_job(job_id):
    with _lock:
        job = _jobs.get(job_id)
        return dict(job) if job else None
