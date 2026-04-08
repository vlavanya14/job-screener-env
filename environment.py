from pydantic import BaseModel
from typing import List, Optional, Dict


# ── Typed Models (OpenEnv spec) ───────────────────────────────────────────────

class Candidate(BaseModel):
    id: str
    name: str
    years_experience: int
    required_skills_match: float   # 0.0 to 1.0
    education_match: bool
    has_gaps: bool
    overqualified: bool
    salary_in_range: bool
    cover_letter_quality: float    # 0.0 to 1.0
    summary: str


class Observation(BaseModel):
    current_candidate: Candidate
    candidates_remaining: int
    total_candidates: int
    step_number: int
    job_title: str
    job_requirements: str


class Action(BaseModel):
    action: str          # "shortlist" | "reject" | "escalate"
    candidate_id: str
    reason: Optional[str] = None


class Reward(BaseModel):
    value: float
    reason: str


# ── Candidate Bank ────────────────────────────────────────────────────────────

EASY_CANDIDATES = [
    Candidate(
        id="e1", name="Alice Chen",
        years_experience=5, required_skills_match=0.95,
        education_match=True, has_gaps=False,
        overqualified=False, salary_in_range=True,
        cover_letter_quality=0.9,
        summary="Senior engineer with perfect skill match, clean history, great communication."
    ),
]

MEDIUM_CANDIDATES = [
    Candidate(
        id="m1", name="Bob Smith",
        years_experience=7, required_skills_match=0.9,
        education_match=True, has_gaps=False,
        overqualified=False, salary_in_range=True,
        cover_letter_quality=0.85,
        summary="Strong candidate, matches well on all dimensions."
    ),
    Candidate(
        id="m2", name="Carol White",
        years_experience=1, required_skills_match=0.2,
        education_match=False, has_gaps=True,
        overqualified=False, salary_in_range=True,
        cover_letter_quality=0.3,
        summary="Very junior, skills mismatch, employment gaps, weak letter."
    ),
    Candidate(
        id="m3", name="David Park",
        years_experience=4, required_skills_match=0.75,
        education_match=True, has_gaps=False,
        overqualified=False, salary_in_range=True,
        cover_letter_quality=0.7,
        summary="Good candidate, decent match, worth shortlisting."
    ),
    Candidate(
        id="m4", name="Eva Martinez",
        years_experience=15, required_skills_match=0.95,
        education_match=True, has_gaps=False,
        overqualified=True, salary_in_range=False,
        cover_letter_quality=0.8,
        summary="Very experienced but overqualified and above salary range — escalate for human decision."
    ),
    Candidate(
        id="m5", name="Frank Lee",
        years_experience=0, required_skills_match=0.1,
        education_match=False, has_gaps=False,
        overqualified=False, salary_in_range=True,
        cover_letter_quality=0.2,
        summary="No experience, very low skill match — clear reject."
    ),
]

HARD_CANDIDATES = [
    Candidate(
        id="h1", name="Grace Kim",
        years_experience=6, required_skills_match=0.88,
        education_match=True, has_gaps=False,
        overqualified=False, salary_in_range=True,
        cover_letter_quality=0.9,
        summary="Strong all-round candidate — shortlist."
    ),
    Candidate(
        id="h2", name="Henry Brown",
        years_experience=3, required_skills_match=0.4,
        education_match=False, has_gaps=True,
        overqualified=False, salary_in_range=True,
        cover_letter_quality=0.6,
        summary="Below average skills, gaps in history — reject."
    ),
    Candidate(
        id="h3", name="Iris Wang",
        years_experience=20, required_skills_match=0.97,
        education_match=True, has_gaps=False,
        overqualified=True, salary_in_range=False,
        cover_letter_quality=0.95,
        summary="Exceptional but overqualified and out of budget — escalate."
    ),
    Candidate(
        id="h4", name="James Patel",
        years_experience=5, required_skills_match=0.82,
        education_match=True, has_gaps=True,
        overqualified=False, salary_in_range=True,
        cover_letter_quality=0.75,
        summary="Good skills but employment gap needs explanation — escalate."
    ),
    Candidate(
        id="h5", name="Karen Liu",
        years_experience=2, required_skills_match=0.15,
        education_match=False, has_gaps=False,
        overqualified=False, salary_in_range=True,
        cover_letter_quality=0.1,
        summary="Clearly unqualified — reject."
    ),
    Candidate(
        id="h6", name="Liam Torres",
        years_experience=4, required_skills_match=0.78,
        education_match=True, has_gaps=False,
        overqualified=False, salary_in_range=True,
        cover_letter_quality=0.8,
        summary="Solid candidate — shortlist."
    ),
    Candidate(
        id="h7", name="Mia Johnson",
        years_experience=8, required_skills_match=0.92,
        education_match=False, has_gaps=False,
        overqualified=False, salary_in_range=True,
        cover_letter_quality=0.85,
        summary="Strong skills but no formal degree — escalate for human review."
    ),
    Candidate(
        id="h8", name="Noah Davis",
        years_experience=0, required_skills_match=0.05,
        education_match=False, has_gaps=True,
        overqualified=False, salary_in_range=False,
        cover_letter_quality=0.1,
        summary="No experience, no match — reject."
    ),
    Candidate(
        id="h9", name="Olivia Garcia",
        years_experience=5, required_skills_match=0.85,
        education_match=True, has_gaps=False,
        overqualified=False, salary_in_range=True,
        cover_letter_quality=0.88,
        summary="Well-rounded candidate — shortlist."
    ),
    Candidate(
        id="h10", name="Peter Wilson",
        years_experience=12, required_skills_match=0.7,
        education_match=True, has_gaps=False,
        overqualified=True, salary_in_range=True,
        cover_letter_quality=0.6,
        summary="Overqualified but in budget — escalate for discussion."
    ),
]

# ── Correct Actions & Logic ───────────────────────────────────────────────────

CORRECT_ACTIONS: Dict[str, str] = {
    "e1": "shortlist",
    "m1": "shortlist", "m2": "reject", "m3": "shortlist",
    "m4": "escalate",  "m5": "reject",
    "h1": "shortlist", "h2": "reject",  "h3": "escalate",
    "h4": "escalate",  "h5": "reject",  "h6": "shortlist",
    "h7": "escalate",  "h8": "reject",  "h9": "shortlist",
    "h10": "escalate",
}

JOB_TITLE = "Software Engineer (Mid-Level)"
JOB_REQUIREMENTS = (
    "3-8 years experience | Strong CS fundamentals | Bachelor's preferred "
    "| Salary band: $90k-$130k | Skills: Python, APIs, system design"
)


# ── Environment Class ─────────────────────────────────────────────────────────

class JobScreenerEnv:
    def __init__(self, task: str = "easy_screen"):
        self.task = task
        self._candidates: List[Candidate] = []
        self._current_index = 0
        self._step = 0
        self._rewards: List[float] = []
        self._done = False

    def _load_candidates(self) -> List[Candidate]:
        if self.task == "easy_screen":
            return list(EASY_CANDIDATES)
        elif self.task == "medium_screen":
            return list(MEDIUM_CANDIDATES)
        else:
            return list(HARD_CANDIDATES)

    def reset(self) -> dict:
        self._candidates = self._load_candidates()
        self._current_index = 0
        self._step = 0
        self._rewards = []
        self._done = False
        return self._make_obs()

    def step(self, action: dict) -> dict:
        if self._done:
            return {
                "observation": self._make_obs(),
                "reward": 0.0,
                "done": True,
                "info": {"error": "Episode already finished"}
            }

        act = Action(**action)
        candidate = self._candidates[self._current_index]
        reward = self._score_action(candidate, act.action)

        self._rewards.append(reward)
        self._step += 1
        self._current_index += 1

        if self._current_index >= len(self._candidates):
            self._done = True

        return {
            "observation": self._make_obs(),
            "reward": round(reward, 2),
            "done": self._done,
            "info": {
                "correct_action": CORRECT_ACTIONS.get(candidate.id, "unknown"),
                "your_action": act.action,
                "candidate_id": candidate.id,
            }
        }

    def state(self) -> dict:
        return {
            "task": self.task,
            "step": self._step,
            "current_index": self._current_index,
            "total_candidates": len(self._candidates),
            "rewards_so_far": self._rewards,
            "average_reward": round(sum(self._rewards) / len(self._rewards), 3) if self._rewards else 0.0,
            "done": self._done,
        }

    def _make_obs(self) -> dict:
        idx = min(self._current_index, len(self._candidates) - 1)
        candidate = self._candidates[idx]
        return Observation(
            current_candidate=candidate,
            candidates_remaining=max(0, len(self._candidates) - self._current_index),
            total_candidates=len(self._candidates),
            step_number=self._step,
            job_title=JOB_TITLE,
            job_requirements=JOB_REQUIREMENTS,
        ).model_dump()

    def _score_action(self, candidate: Candidate, action: str) -> float:
        correct = CORRECT_ACTIONS.get(candidate.id, "reject")

        # Perfect action
        if action == correct:
            return 1.0

        # Partial credit logic
        skills = candidate.required_skills_match
        exp = candidate.years_experience
        overq = candidate.overqualified
        gap = candidate.has_gaps
        sal = candidate.salary_in_range

        # Borderline cases — close decisions get partial credit
        if correct == "escalate" and action == "shortlist":
            # Not terrible — at least didn't reject a complex case
            return 0.4
        if correct == "escalate" and action == "reject":
            # Missed a nuanced case
            return 0.2
        if correct == "shortlist" and action == "escalate":
            # Overly cautious but not wrong
            return 0.5
        if correct == "reject" and action == "escalate":
            # Wasted human time but didn't wrongly shortlist
            return 0.3
        if correct == "reject" and action == "shortlist":
            # Worst outcome — shortlisting a bad candidate
            return 0.0
        if correct == "shortlist" and action == "reject":
            # Missed a good candidate
            return 0.0

        return 0.1
