"""
SQLAlchemy ORM models for the RAG Discovery Engine PostgreSQL database.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    DateTime,
    Float,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB  # Keeping for reference, but not using
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


class FeedbackRecordModel(Base):
    """
    Structured storage for cleaned, authentic feedback records.
    Matches architecture §6.1.
    """
    __tablename__ = "feedback_records"

    feedback_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    author_id_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    
    content_raw: Mapped[str] = mapped_column(Text, nullable=False)
    content_cleaned: Mapped[str] = mapped_column(Text, nullable=False)
    
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ingestion_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    platform_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    
    # NLP & Enrichment Fields (Phase 3)
    sentiment_scores: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    purchase_barriers: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    user_behaviours: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    relevance: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    topic_cluster_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    user_segment_tags: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    opportunity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    # Deduplication
    dedup_fingerprint: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)


class TopicClusterModel(Base):
    """
    Stores BERTopic outputs for emerging theme discovery.
    """
    __tablename__ = "topic_clusters"

    cluster_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cluster_label: Mapped[str] = mapped_column(String(255), nullable=False)
    keywords: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)  # list of keywords
    record_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    avg_sentiment: Mapped[float | None] = mapped_column(Float, nullable=True)
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class OpportunityMatrixModel(Base):
    """
    Stores aggregated friction metrics for the Analytics Dashboard.
    """
    __tablename__ = "opportunity_matrix"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    purchase_barrier: Mapped[str] = mapped_column(String(100), nullable=False)
    barrier_label: Mapped[str] = mapped_column(String(100), nullable=False)
    total_mentions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    frequency_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estimated_conversion_impact: Mapped[float | None] = mapped_column(Float, nullable=True)
    affected_segments: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    opportunity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    last_computed: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class IngestionRunModel(Base):
    """
    Logs metadata for every pipeline run.
    """
    __tablename__ = "ingestion_runs"

    run_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    source: Mapped[str | None] = mapped_column(String(50), nullable=True)
    records_fetched: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    records_inserted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    exact_dedup_dropped: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    near_dedup_dropped: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    synthetic_dropped: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class QuarantineRecordModel(Base):
    """
    Stores records flagged by the synthetic/bot filters.
    """
    __tablename__ = "quarantine_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    content_raw: Mapped[str] = mapped_column(Text, nullable=False)
    flag_reason: Mapped[str] = mapped_column(String(255), nullable=False)
    flag_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    dedup_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
