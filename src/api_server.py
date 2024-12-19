from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from task_parser import TaskParser
import uvicorn
from typing import Optional
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
from fastapi_cache.backends.inmemory import InMemoryBackend

app = FastAPI(title="Task Parser API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

parser = TaskParser()

@app.on_event("startup")
async def startup():
    FastAPICache.init(InMemoryBackend())

class TaskInput(BaseModel):
  text: str

class TaskOutput(BaseModel):
  name: str
  description: str
  due_date: str | None
  completion_date: str | None
  status: str
  url: str | None

@app.post("/parse-task", response_model=TaskOutput, status_code=201)
@cache(expire=3600)
async def parse_task(task_input: TaskInput):
    try:
        result = parser.parse_task(task_input.text)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.get("/health")
async def health_check():
  return {"status": "healthy"}

if __name__ == "__main__":
  uvicorn.run(app, host="0.0.0.0", port=8080)