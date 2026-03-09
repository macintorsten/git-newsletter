"""
Abstract base class for all newsletter data sources.

New sources (GitLab, Jira, Jenkins, …) should subclass BaseSource and
implement ``fetch()``, which returns a plain dict of raw data.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseSource(ABC):
    """Base class for all data sources."""

    #: Short identifier used in log messages and the orchestrator's result dict.
    source_id: str = "base"

    def __init__(self, config: dict[str, Any] | None = None):
        self.config: dict[str, Any] = config or {}

    @abstractmethod
    def fetch(self) -> dict[str, Any]:
        """
        Fetch data and return it as a plain dict.

        For agent workflows the agent writes these results directly to
        ``session_store`` via SQL.  For the CLI the orchestrator collects
        the dict and uses it to build the newsletter template.
        """

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} source_id={self.source_id!r}>"
