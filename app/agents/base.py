from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SharedState:
    goal: str
    context: dict[str, Any]
    artifacts: dict[str, Any] = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    decisions: list[dict[str, Any]] = field(default_factory=list)
    timeline: list[str] = field(default_factory=list)


@dataclass
class AgentResult:
    stage: str
    summary: str
    artifact_key: str
    artifact: dict[str, Any]
    new_issues: list[str] = field(default_factory=list)
    new_risks: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    decision: dict[str, Any] | None = None


class BaseAgent:
    name: str = "base_agent"
    role: str = "base"
    capabilities: list[str] = []

    def describe(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "role": self.role,
            "capabilities": self.capabilities,
        }

    def act(self, state: SharedState) -> AgentResult:
        raise NotImplementedError
