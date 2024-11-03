from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from task_parser import TaskParser
import uvicorn

app = FastAPI(title="Task Parser API")
parser = TaskParser()

class TaskInput(BaseModel):
  text: str

class TaskOutput(BaseModel):
  name: str
  description: str
  due_date: str | None
  completion_date: str | None
  status: str
  url: str | None

@app.post("/parse-task", response_model=TaskOutput)
async def parse_task(task_input: TaskInput):
  try:
      result = parser.parse_task(task_input.text)
      return result
  except Exception as e:
      raise HTTPException(status_code=400, detail=str(e))

@app.get("/health")
async def health_check():
  return {"status": "healthy"}

if __name__ == "__main__":
  uvicorn.run(app, host="0.0.0.0", port=8080)