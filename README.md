---
title: Job Screener Env
emoji: 🚀
colorFrom: blue
colorTo: green
sdk: docker
app_file: app.py
pinned: false
---
An OpenEnv environment where an AI agent screens job applications and decides:
**shortlist**, **reject**, or **escalate to human review**.

## Why This Matters
HR teams process hundreds of applications per role. An AI agent that can accurately triage candidates saves significant time while ensuring qualified candidates aren't missed.

## Tasks

| Task | Difficulty | Candidates | Description |
|------|-----------|-----------|-------------|
| `easy_screen` | Easy | 1 | Single obvious candidate |
| `medium_screen` | Medium | 5 | Mixed pool with clear and borderline cases |
| `hard_screen` | Hard | 10 | Complex cases with conflicting signals |

## Action Space

| Action | When to use |
|--------|------------|
| `shortlist` | Strong match: good skills, experience, education, salary fit |
| `reject` | Clear mismatch: low skills, no experience, obvious disqualifier |
| `escalate` | Borderline: overqualified, employment gaps, salary out of range — needs human |

## Observation Space

Each step the agent receives:
- `current_candidate`: name, years_experience, required_skills_match (0-1), education_match, has_gaps, overqualified, salary_in_range, cover_letter_quality (0-1), summary
- `candidates_remaining`: how many left in queue
- `job_title`: position being hired for
- `job_requirements`: requirements string

## Reward Function

| Outcome | Reward |
|---------|--------|
| Correct action | 1.0 |
| Shortlisted when should escalate | 0.4 |
| Escalated when should shortlist | 0.5 |
| Rejected when should escalate | 0.2 |
| Escalated when should reject | 0.3 |
| Shortlisted a bad candidate | 0.0 |
| Rejected a good candidate | 0.0 |

## Baseline Scores

| Task | Score |
|------|-------|
| easy_screen | ~1.0 |
| medium_screen | ~1.0|
| hard_screen | ~0.810 |
| Overall average | ~0.937 |

## Setup

### Local (without Docker)
```bash
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 7860
```

### Docker
```bash
docker build -t job-screener-env .
docker run -p 7860:7860 job-screener-env
```

### Test it works
```bash
curl -X POST http://localhost:7860/reset \
  -H "Content-Type: application/json" \
  -d '{"task": "easy_screen"}'
```

### Run inference
```bash
export HF_TOKEN=your_token_here
export ENV_URL=http://localhost:7860
python inference.py
```

## API Endpoints

- `POST /reset` — Start new episode. Body: `{"task": "easy_screen"}`
- `POST /step` — Take action. Body: `{"action": "shortlist", "candidate_id": "e1", "task": "easy_screen"}`
- `GET /state` — Current episode state. Query: `?task=easy_screen`
- `GET /health` — Health check
