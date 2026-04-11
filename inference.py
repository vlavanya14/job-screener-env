"""
inference.py - Job Screener OpenEnv Baseline
"""

import os
import sys
import requests
from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN", "")
ENV_URL = os.getenv("ENV_URL", "http://localhost:7860")

client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN or "dummy")

TASKS = ["easy_screen", "medium_screen", "hard_screen"]
VALID_ACTIONS = ["shortlist", "reject", "escalate"]

SYSTEM_PROMPT = """You are an expert HR recruiter screening job applications.

The job is: Software Engineer (Mid-Level)
Requirements: 3-8 years experience | Strong CS fundamentals | Bachelor's preferred

Reply with only one word: shortlist, reject, or escalate"""


def log_start(task, model):
    print(f"[START] task={task} env=job-screener-env model={model}", flush=True)


def log_step(step, action, reward, done, error=None):
    err = error if error else "null"
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={err}", flush=True)


def log_end(success, steps, score, rewards):
    r_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={r_str}", flush=True)


def get_action(candidate: dict) -> str:
    try:
        resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": str(candidate)},
            ],
            max_tokens=5,
            temperature=0.0,
        )
        word = resp.choices[0].message.content.strip().lower().split()[0]
        return word if word in VALID_ACTIONS else "escalate"
    except Exception:
        return "escalate"


def run_task(task: str) -> float:
    try:
        log_start(task, MODEL_NAME)

        r = requests.post(f"{ENV_URL}/reset", json={"task": task}, timeout=10)
        result = r.json()

        obs = result.get("observation", {})
        done = result.get("done", False)
        rewards = []
        step = 0

        while not done:
            try:
                candidate = obs.get("current_candidate")
                if not candidate:
                    break

                action = get_action(candidate)
                step += 1

                resp = requests.post(f"{ENV_URL}/step", json={
                    "action": action,
                    "candidate_id": candidate.get("id"),
                    "reason": "auto",
                    "task": task,
                }, timeout=10)

                data = resp.json()

                reward = data.get("reward", 0.0)
                done = data.get("done", False)
                obs = data.get("observation", {})
                error = data.get("info", {}).get("error")

                rewards.append(reward)
                log_step(step, action, reward, done, error)

            except Exception as e:
                print("[DEBUG] step error:", e, flush=True)
                break

        score = sum(rewards) / len(rewards) if rewards else 0.0
        score = round(score, 3)
        log_end(True, step, score, rewards)
        return score

    except Exception as e:
        print("[DEBUG] run_task failed:", e, flush=True)
        log_end(False, 0, 0.0, [])
        return 0.0


if __name__ == "__main__":
    try:
        all_scores = []
        for task in TASKS:
            score = run_task(task)
            all_scores.append(score)

        overall = sum(all_scores) / len(all_scores) if all_scores else 0.0
        print(f"[DEBUG] Overall average score: {overall:.3f}", flush=True)

    except Exception as e:
        print("[ERROR]", e, flush=True)
        print("[END] success=false steps=0 score=0.0 rewards=")
        sys.exit(0)
