from __future__ import annotations

from pydantic import BaseModel


class Unit(BaseModel):
    id: str
    name: str
    description: str = ""
    hard_deps: list[str] = []
    soft_deps: list[str] = []


class EngineerRefinement(BaseModel):
    architecture: str = ""
    invariants: list[str] = []
    technical_constraints: list[str] = []
    interfaces: str = ""
    edge_cases: list[str] = []
    decomposition: list[Unit] = []
