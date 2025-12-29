from fastapi import FastAPI, Query
from .client.rq_client import queue
from .queues.worker import process_query

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
    result = job.return_value()
    return {"result": result} 