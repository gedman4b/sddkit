from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class Intent(BaseModel):
    summary: str
    details: str = ""


class Constraint(BaseModel):
    id: str = ""
    text: str
    kind: Literal["must", "must-not", "should", "should-not"] = "must"


class AcceptanceCriterion(BaseModel):
    id: str
    text: str
    input_pattern: str | None = None


class NonGoal(BaseModel):
    id: str = ""
    text: str


class Dependency(BaseModel):
    name: str
    kind: Literal["hard", "soft"] = "hard"
    description: str = ""


class Issue(BaseModel):
    severity: Literal["error", "warning", "info"]
    component: str
    message: str


class ValidationReport(BaseModel):
    is_operational: bool
    issues: list[Issue] = []
