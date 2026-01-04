from fastapi import FastAPI, Query
from .rq_client import queue
from .worker import process_query

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "RAG Queue Server is running"}

@app.post("/chat")
def chat(qry: str = Query(..., description="The chat query of the user")):
    job = queue.enqueue(process_query, qry)
    return {"status": "queued", "job_id": job.id}

@app.get("/job_status")
def get_result(job_id: str = Query(..., description="the job id")):
    job = queue.fetch_job(job_id=job_id)
    if not job:
        return {"status": "not_found"}
    
    if job.is_failed:
        return {"status": "failed", "error": str(job.exc_info)}
    
    if job.is_finished:
        return {"status": "completed", "result": job.result}
    
    if job.is_started:
        return {"status": "running"}
    
    return {"status": "queued"}