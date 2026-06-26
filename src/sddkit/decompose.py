"""Decomposition graph helpers.

decompose_spec() extracts the Unit list from a Spec's EngineerRefinement,
validates the dependency graph (no unknown references, no cycles), and returns
the units in topological order (hard dependencies first).

Raises RefinementIncompleteError for:
  - refinement=None (no engineer refinement present)
  - a hard_dep or soft_dep that names an unknown unit id
  - a cycle in the dependency graph (cycle is named in the message)
"""
from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING

from sddkit.models.errors import RefinementIncompleteError
from sddkit.models.refinement import Unit

if TYPE_CHECKING:
    from sddkit.models.spec import Spec


def decompose_spec(spec: "Spec") -> list[Unit]:
    if spec.refinement is None:
        raise RefinementIncompleteError(
            "decompose() requires engineer refinement. "
            "Populate Spec.refinement with an EngineerRefinement before calling decompose()."
        )

    units = spec.refinement.decomposition
    if not units:
        return []

    unit_by_id: dict[str, Unit] = {u.id: u for u in units}

    # Validate all referenced ids exist.
    for unit in units:
        for dep_id in unit.hard_deps + unit.soft_deps:
            if dep_id not in unit_by_id:
                raise RefinementIncompleteError(
                    f"Unit '{unit.id}' references unknown dependency '{dep_id}'. "
                    "All dependency ids must correspond to a unit in the decomposition."
                )

    # Topological sort via Kahn's algorithm (hard + soft deps as edges).
    # Build adjacency and in-degree over all deps.
    in_degree: dict[str, int] = {u.id: 0 for u in units}
    dependents: dict[str, list[str]] = {u.id: [] for u in units}

    for unit in units:
        for dep_id in unit.hard_deps + unit.soft_deps:
            # dep_id must come before unit.id
            dependents[dep_id].append(unit.id)
            in_degree[unit.id] += 1

    queue: deque[str] = deque(uid for uid, deg in in_degree.items() if deg == 0)
    ordered: list[str] = []

    while queue:
        uid = queue.popleft()
        ordered.append(uid)
        for dependent_id in dependents[uid]:
            in_degree[dependent_id] -= 1
            if in_degree[dependent_id] == 0:
                queue.append(dependent_id)

    if len(ordered) != len(units):
        # Cycle detected — name the participating ids.
        cycle_ids = [uid for uid, deg in in_degree.items() if deg > 0]
        raise RefinementIncompleteError(
            f"Cycle detected in decomposition dependency graph. "
            f"Participating units: {', '.join(sorted(cycle_ids))}. "
            "Remove the cycle before calling decompose()."
        )

    return [unit_by_id[uid] for uid in ordered]
