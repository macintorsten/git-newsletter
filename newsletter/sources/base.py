"""
Abstract base class for all newsletter data sources.

New sources (GitLab, Jira, Jenkins, …) should subclass BaseSource and
implement `fetch()`.  The orchestrator discovers all registered sources
and calls `fetch()` on each one, writing the results to the session database.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from newsletter.models import SessionDatabase


class BaseSource(ABC):
    """Base class for all data sources."""

    #: Short identifier used in session_database["raw_data"] and log messages.
    source_id: str = "base"

    def __init__(self, config: dict[str, Any] | None = None):
        self.config: dict[str, Any] = config or {}

    @abstractmethod
    def fetch(self, db: SessionDatabase) -> None:
        """
        Fetch data and write results into *db*.

        Implementations should write their findings to
        ``db.raw_data.<source_id>`` and append progress messages via
        ``newsletter.session_db.log(db, ...)``.
        """

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} source_id={self.source_id!r}>"
