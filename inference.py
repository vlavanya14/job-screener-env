"""
inference.py - Job Screener OpenEnv Baseline
Runs all 3 tasks and emits [START] [STEP] [END] logs.
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
Requirements: 3-8 years experience | Strong CS fundamentals | Bachelor's preferred | Salary: $90k-$130k

Given a candidate profile, respond with EXACTLY one word:
- shortlist  → good match, move forward
- reject     → clearly unqualified or poor match  
- escalate   → borderline case needing human review (overqualified, gaps, salary mismatch)

Reply with only one word: shortlist, reject, or escalate"""


def log_start(task, model):
    print(f"[START] task={task} env=job-screener-env model={model}", flush=True)

def log_step(step, action, reward, done, error=None):
    err = error if error else "null"
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={err}", flush=True)

def log_end(success, steps, score, rewards):
    r_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={r_str}", flush=True)


def get_action(candidate: dict, job_requirements: str) -> str:
    prompt = f"""Candidate: {candidate['name']}
Experience: {candidate['years_experience']} years
Skills match: {candidate['required_skills_match']*100:.0f}%
Education match: {candidate['education_match']}
Employment gaps: {candidate['has_gaps']}
Overqualified: {candidate['overqualified']}
Salary in range: {candidate['salary_in_range']}
Cover letter quality: {candidate['cover_letter_quality']*100:.0f}%
Summary: {candidate['summary']}

Decision?"""
    try:
        resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            max_tokens=10,
            temperature=0.0,
        )
        word = resp.choices[0].message.content.strip().lower().split()[0]
        return word if word in VALID_ACTIONS else "escalate"
    except Exception as e:
        print(f"[DEBUG] LLM error: {e}", flush=True)
        if candidate['required_skills_match'] >= 0.75 and not candidate['overqualified']:
            return "shortlist"
        elif candidate['required_skills_match'] < 0.4:
            return "reject"
        else:
            return "escalate"


def run_task(task: str) -> float:
    log_start(task, MODEL_NAME)

    try:
        r = requests.post(f"{ENV_URL}/reset", json={"task": task}, timeout=30)
        result = r.json()
    except Exception as e:
        print(f"[DEBUG] Reset failed: {e}", flush=True)
        log_end(False, 0, 0.0, [])
        return 0.0

    obs = result.get("observation", {})
    done = result.get("done", False)
    rewards = []
    step = 0

    while not done:
        try:
            candidate = obs["current_candidate"]
        except:
            break

        action = get_action(candidate, obs.get("job_requirements", ""))
        step += 1

        try:
            resp = requests.post(f"{ENV_URL}/step", json={
                "action": action,
                "candidate_id": candidate.get("id"),
                "reason": f"Automated decision: {action}",
                "task": task,
            }, timeout=30)
            data = resp.json()
        except Exception as e:
            print(f"[DEBUG] Step failed: {e}", flush=True)
            break

        reward = data.get("reward", 0.0)
        done = data.get("done", False)
        obs = data.get("observation", obs)
        error = data.get("info", {}).get("error")

        rewards.append(reward)
        log_step(step, action, reward, done, error)

    score = sum(rewards) / len(rewards) if rewards else 0.0
    score = round(min(max(score, 0.0), 1.0), 3)
    success = score >= 0.5
    log_end(success, step, score, rewards)
    return score


def safe_exit():
    print("[END] success=false steps=0 score=0.0 rewards=")
    sys.exit(0)


if __name__ == "__main__":
    try:
        print(f"[DEBUG] Connecting to env at {ENV_URL}", flush=True)
        all_scores = []
        for task in TASKS:
            score = run_task(task)
            all_scores.append(score)
            print(f"[DEBUG] {task} score: {score:.3f}", flush=True)

        overall = sum(all_scores) / len(all_scores)
        print(f"[DEBUG] Overall average score: {overall:.3f}", flush=True)

    except Exception as e:
        print("[ERROR]", e, flush=True)
        safe_exit()
