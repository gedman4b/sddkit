from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from sddkit.models.components import (
    AcceptanceCriterion,
    Constraint,
    Dependency,
    Intent,
    NonGoal,
    ValidationReport,
)
from sddkit.models.refinement import EngineerRefinement, Unit


class Spec(BaseModel):
    name: str
    identifier: str
    version: str
    status: Literal["draft", "active", "deprecated"]
    intent: Intent
    constraints: list[Constraint] = []
    acceptance_criteria: list[AcceptanceCriterion] = []
    non_goals: list[NonGoal] = []
    dependencies: list[Dependency] = []
    refinement: EngineerRefinement | None = None

    def validate_operational(self) -> ValidationReport:
        raise NotImplementedError("sddkit.validation (U5) not yet implemented")

    def is_operational(self) -> bool:
        raise NotImplementedError("sddkit.validation (U5) not yet implemented")

    def to_yaml(self) -> str:
        from sddkit.serialize.yaml_io import spec_to_yaml

        return spec_to_yaml(self)

    @classmethod
    def from_yaml(cls, text: str) -> "Spec":
        from sddkit.serialize.yaml_io import spec_from_yaml

        return spec_from_yaml(text)

    def to_json(self) -> str:
        from sddkit.serialize.json_io import spec_to_json

        return spec_to_json(self)

    @classmethod
    def from_json(cls, text: str) -> "Spec":
        from sddkit.serialize.json_io import spec_from_json

        return spec_from_json(text)

    def to_markdown(self) -> str:
        from sddkit.serialize.markdown_io import spec_to_markdown

        return spec_to_markdown(self)

    @classmethod
    def from_markdown(cls, text: str) -> "Spec":
        from sddkit.serialize.markdown_io import spec_from_markdown

        return spec_from_markdown(text)

    def to_agents_md(self, identity: str | None = None) -> str:
        raise NotImplementedError("sddkit.emit.agents (U6) not yet implemented")

    def emit_skill_file(
        self,
        skill_type: Literal[
            "spec_ingestion", "constrained_execution", "self_verification"
        ],
    ) -> str:
        raise NotImplementedError("sddkit.emit.skills (U7) not yet implemented")

    def decompose(self) -> list[Unit]:
        raise NotImplementedError("sddkit.decompose (U8) not yet implemented")

    def derive_tests(
        self, framework: Literal["pytest"] = "pytest"
    ) -> dict[str, str]:
        raise NotImplementedError("sddkit.tests.derive (U9) not yet implemented")
