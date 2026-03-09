"""
Data models for the newsletter editor pipeline.

All models use plain dataclasses so they are serialisable to JSON without
an extra dependency.  If Pydantic is available it is preferred for validation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any


# ---------------------------------------------------------------------------
# Commit / branch models
# ---------------------------------------------------------------------------

@dataclass
class CommitRecord:
    sha: str
    short_sha: str
    author_name: str
    author_email: str
    committer_name: str
    committer_email: str
    timestamp: str          # ISO-8601
    message: str
    diff_summary: str       # human-readable "+N -M in K files"
    diff_patch: str = ""    # full unified diff; may be large


@dataclass
class BranchActivity:
    name: str
    last_commit_sha: str
    last_commit_timestamp: str  # ISO-8601
    last_author: str
    commits_in_period: int
    ahead_of_default: int = 0
    behind_default: int = 0
    is_merged: bool = False


@dataclass
class StaleBranch:
    name: str
    last_commit_sha: str
    last_commit_timestamp: str  # ISO-8601
    last_author: str
    age_days: int


# ---------------------------------------------------------------------------
# Article / research models
# ---------------------------------------------------------------------------

@dataclass
class CommitArticle:
    id: str
    commit_shas: list[str]
    title: str
    body_markdown: str
    author_credits: list[str]
    deep_dive_suggested: bool = False
    deep_dive_question: str | None = None


@dataclass
class ResearchTask:
    id: str
    question: str
    context: str            # commit SHA or article id that triggered this
    max_words: int = 150
    status: str = "pending" # "pending" | "done" | "failed"


@dataclass
class ResearchResult:
    id: str
    question: str
    summary_markdown: str
    learn_more_url: str
    sources: list[str]


# ---------------------------------------------------------------------------
# Editorial decisions
# ---------------------------------------------------------------------------

@dataclass
class EditorialDecision:
    selected_article_ids: list[str] = field(default_factory=list)
    selected_deep_dive_ids: list[str] = field(default_factory=list)   # max 3


# ---------------------------------------------------------------------------
# Session database
# ---------------------------------------------------------------------------

@dataclass
class SessionMetadata:
    repo: str = ""
    branch: str = "main"
    period_days: int = 7
    stale_after_days: int = 30
    generated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class SessionStatus:
    git_research: str = "pending"     # pending | done | failed
    commit_analysis: str = "pending"
    web_research: str = "pending"
    newsletter_writing: str = "pending"


@dataclass
class RawGitData:
    repo: str = ""
    default_branch: str = "main"
    period_days: int = 7
    stale_after_days: int = 30
    commits: list[dict[str, Any]] = field(default_factory=list)
    branch_activity: list[dict[str, Any]] = field(default_factory=list)
    stale_branches: list[dict[str, Any]] = field(default_factory=list)
    merged_branches: list[str] = field(default_factory=list)


@dataclass
class RawData:
    git: dict[str, Any] = field(default_factory=dict)
    # Future sources: gitlab, jira, jenkins, etc.


@dataclass
class ArticleStore:
    commits: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class OutputData:
    newsletter_markdown: str = ""
    output_path: str = "newsletter_output.md"


@dataclass
class SessionDatabase:
    """
    The shared session database passed between all agents during a pipeline run.

    Every agent reads from and writes to this object.  The orchestrator
    persists it as a JSON file so agents can be resumed or inspected.
    """
    metadata: SessionMetadata = field(default_factory=SessionMetadata)
    status: SessionStatus = field(default_factory=SessionStatus)
    raw_data: RawData = field(default_factory=RawData)
    articles: ArticleStore = field(default_factory=ArticleStore)
    deep_dive_candidates: list[dict[str, Any]] = field(default_factory=list)
    research_queue: list[dict[str, Any]] = field(default_factory=list)
    research_results: list[dict[str, Any]] = field(default_factory=list)
    editorial: EditorialDecision = field(default_factory=EditorialDecision)
    output: OutputData = field(default_factory=OutputData)
    logs: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SessionDatabase":
        db = cls()
        db.metadata = SessionMetadata(**data.get("metadata", {}))
        db.status = SessionStatus(**data.get("status", {}))

        raw = data.get("raw_data", {})
        db.raw_data = RawData(git=raw.get("git", {}))

        articles = data.get("articles", {})
        db.articles = ArticleStore(commits=articles.get("commits", []))

        ed = data.get("editorial", {})
        db.editorial = EditorialDecision(
            selected_article_ids=ed.get("selected_article_ids", []),
            selected_deep_dive_ids=ed.get("selected_deep_dive_ids", []),
        )

        out = data.get("output", {})
        db.output = OutputData(
            newsletter_markdown=out.get("newsletter_markdown", ""),
            output_path=out.get("output_path", "newsletter_output.md"),
        )

        db.deep_dive_candidates = data.get("deep_dive_candidates", [])
        db.research_queue = data.get("research_queue", [])
        db.research_results = data.get("research_results", [])
        db.logs = data.get("logs", [])
        return db

    @classmethod
    def from_json(cls, json_str: str) -> "SessionDatabase":
        return cls.from_dict(json.loads(json_str))
