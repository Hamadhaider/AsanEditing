import asyncio
from pathlib import Path
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from .config import FRONTEND_ORIGIN, OUTPUT_DIR
from .models import CreateJob
from .state import create_job, get_job
from .worker import produce
from .gemini_browser import browser

app=FastAPI(title="AsanEditing API",version="1.0.0")
app.add_middleware(CORSMiddleware,allow_origins=[FRONTEND_ORIGIN,"http://127.0.0.1:3000"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])

@app.get("/api/health")
def health(): return {"ok":True,"name":"AsanEditing"}

@app.post("/api/gemini/connect")
async def connect_gemini():
    try: return await browser.connect()
    except Exception as e: raise HTTPException(500,str(e))

@app.post("/api/jobs")
async def start_job(payload:CreateJob,background:BackgroundTasks):
    job_id=create_job(payload)
    background.add_task(produce,job_id,payload)
    return {"id":job_id,"status":"queued"}

@app.get("/api/jobs/{job_id}")
def job_status(job_id:str):
    job=get_job(job_id)
    if not job: raise HTTPException(404,"Job not found")
    return job

@app.get("/download/{job_id}")
def download(job_id:str):
    path=OUTPUT_DIR/job_id/"AsanEditing_final.mp4"
    if not path.exists(): raise HTTPException(404,"Video is not ready")
    return FileResponse(path,media_type="video/mp4",filename="AsanEditing_final.mp4")

@app.on_event("shutdown")
async def shutdown():
    await browser.close()
