from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from environment import JobScreenerEnv

app = FastAPI(title="Job Screener OpenEnv", version="1.0.0")

_envs = {}

def get_env(task: str) -> JobScreenerEnv:
    if task not in _envs:
        _envs[task] = JobScreenerEnv(task=task)
    return _envs[task]


class ResetRequest(BaseModel):
    task: Optional[str] = "easy_screen"

class StepRequest(BaseModel):
    action: str
    candidate_id: str
    reason: Optional[str] = None
    task: Optional[str] = "easy_screen"


@app.post("/reset")
def reset(req: ResetRequest = ResetRequest()):
    env = get_env(req.task)
    obs = env.reset()
    return {"observation": obs, "done": False, "task": req.task}

@app.post("/step")
def step(req: StepRequest):
    env = get_env(req.task)
    result = env.step({
        "action": req.action,
        "candidate_id": req.candidate_id,
        "reason": req.reason,
    })
    return result

@app.get("/state")
def state(task: str = "easy_screen"):
    env = get_env(task)
    return env.state()

@app.get("/health")
def health():
    return {"status": "ok", "tasks": ["easy_screen", "medium_screen", "hard_screen"]}

@app.get("/")
def root():
    return {"name": "job-screener-env", "version": "1.0.0", "status": "running"}
