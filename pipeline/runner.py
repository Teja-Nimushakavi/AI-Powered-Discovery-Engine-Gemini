"""
Ingestion Pipeline Runner.

Orchestrates the full Phase 2 ETL pipeline:
  Extract: Read JSONL from data/raw/
  Transform: Clean, Filter, Deduplicate
  Load: Insert into PostgreSQL via SQLAlchemy
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config.settings import get_settings
from models.db import FeedbackRecordModel, IngestionRunModel, QuarantineRecordModel
from nlp.cleaner import TextCleaner
from nlp.analyzer import NLPAnalyzer
from pipeline.dedup import DedupEngine
from pipeline.synthetic_filter import SyntheticFilter
from vectordb.indexer import VectorIndexer

logger = logging.getLogger(__name__)


class IngestionPipeline:
    """
    Coordinates the execution of the Data Quality Gate and DB load.
    """

    def __init__(self) -> None:
        self.settings = get_settings()
        
        # Setup Database
        self.engine = create_engine(self.settings.postgres_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)
        
        # Initialize pipeline components
        self.cleaner = TextCleaner()
        self.dedup_engine = DedupEngine()
        self.synthetic_filter = SyntheticFilter()
        self.analyzer = NLPAnalyzer(device=-1) # Force CPU for cross-platform stability
        self.indexer = VectorIndexer()

    def _load_existing_fingerprints(self, session: Any) -> None:
        """Prime the exact-dedup engine with fingerprints already in DB."""
        # Note: Near-dedup LSH index is not persisted across runs in this simple implementation,
        # but exact-dedup fingerprints are loaded to prevent identical duplicates across runs.
        fingerprints = session.query(FeedbackRecordModel.dedup_fingerprint).all()
        for (fp,) in fingerprints:
            self.dedup_engine.seen_fingerprints.add(fp)
            
        quarantine_fps = session.query(QuarantineRecordModel.dedup_fingerprint).all()
        for (fp,) in quarantine_fps:
            self.dedup_engine.seen_fingerprints.add(fp)

        logger.info("Loaded %d existing fingerprints for exact deduplication.", len(self.dedup_engine.seen_fingerprints))

    def process_file(self, file_path: Path) -> dict[str, int]:
        """
        Process a single JSONL file and insert records to DB.
        
        Returns:
            Dictionary of metrics (fetched, inserted, exactly dropped, near dropped, synthetic).
        """
        metrics = {
            "fetched": 0,
            "inserted": 0,
            "exact_dropped": 0,
            "near_dropped": 0,
            "synthetic_dropped": 0,
            "invalid_language": 0,
        }
        
        source_name = file_path.stem.rsplit("_", 2)[0]
        
        valid_records = []
        quarantine_records = []

        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                    
                metrics["fetched"] += 1
                record = json.loads(line)
                
                # 1. Clean & Detect Language
                raw_text = record["content_raw"]
                clean_result = self.cleaner.process_record(raw_text)
                
                if not clean_result["is_supported_language"]:
                    metrics["invalid_language"] += 1
                    continue
                    
                cleaned_text = clean_result["content_cleaned"]
                record["content_cleaned"] = cleaned_text
                
                # 2. Synthetic/Bot Filter
                is_flagged, reason, score = self.synthetic_filter.evaluate(cleaned_text)
                if is_flagged:
                    metrics["synthetic_dropped"] += 1
                    quarantine_records.append(
                        QuarantineRecordModel(
                            source=record["source"],
                            content_raw=raw_text,
                            flag_reason=reason,
                            flag_score=score,
                            dedup_fingerprint=record["dedup_fingerprint"]
                        )
                    )
                    continue
                
                # 3. Deduplication (Exact + Near)
                # For Phase 2, we simulate Exact and Near separately in metrics for clarity,
                # but DedupEngine handles both. We check exact first manually for metrics logging.
                fingerprint = record["dedup_fingerprint"]
                if fingerprint in self.dedup_engine.seen_fingerprints:
                    metrics["exact_dropped"] += 1
                    continue
                    
                is_duplicate = self.dedup_engine.is_duplicate(record["feedback_id"], cleaned_text, fingerprint)
                if is_duplicate:
                    metrics["near_dropped"] += 1
                    continue
                
                # Passed all gates!
                # Parse timestamps
                try:
                    ts = datetime.fromisoformat(record["timestamp"])
                except Exception:
                    ts = datetime.now(timezone.utc)
                    
                ingest_ts = datetime.now(timezone.utc)

                valid_records.append(
                    FeedbackRecordModel(
                        feedback_id=record["feedback_id"],
                        source=record["source"],
                        source_url=record["source_url"],
                        author_id_hash=record["author_id_hash"],
                        content_raw=raw_text,
                        content_cleaned=cleaned_text,
                        timestamp=ts,
                        ingestion_timestamp=ingest_ts,
                        platform_metadata=record["platform_metadata"],
                        dedup_fingerprint=fingerprint
                    )
                )

        # Bulk insert to DB
        with self.Session() as session:
            if valid_records:
                session.bulk_save_objects(valid_records)
                metrics["inserted"] = len(valid_records)
                
            if quarantine_records:
                session.bulk_save_objects(quarantine_records)
                
            # Log run
            run_log = IngestionRunModel(
                source=source_name,
                records_fetched=metrics["fetched"],
                records_inserted=metrics["inserted"],
                exact_dedup_dropped=metrics["exact_dropped"],
                near_dedup_dropped=metrics["near_dropped"],
                synthetic_dropped=metrics["synthetic_dropped"]
            )
            session.add(run_log)
            session.commit()
            
        return metrics

    def run_all(self) -> None:
        """Run the ingestion pipeline on all raw JSONL files."""
        data_dir = self.settings.raw_data_path
        
        if not data_dir.exists():
            logger.warning("Data directory %s does not exist.", data_dir)
            return

        jsonl_files = list(data_dir.glob("*.jsonl"))
        if not jsonl_files:
            logger.info("No JSONL files found in %s", data_dir)
            return

        logger.info("Starting Ingestion Pipeline for %d files.", len(jsonl_files))
        
        with self.Session() as session:
            self._load_existing_fingerprints(session)

        total_inserted = 0
        for file_path in jsonl_files:
            logger.info("Processing file: %s", file_path.name)
            metrics = self.process_file(file_path)
            logger.info(
                "Results for %s: Fetched=%d, Inserted=%d, ExactDup=%d, NearDup=%d, Synthetic=%d, InvalidLang=%d",
                file_path.name,
                metrics["fetched"],
                metrics["inserted"],
                metrics["exact_dropped"],
                metrics["near_dropped"],
                metrics["synthetic_dropped"],
                metrics["invalid_language"]
            )
            total_inserted += metrics["inserted"]
            
            # Optionally archive file to processed/ folder
            # For this Phase, we keep it simple.

        logger.info("Ingestion complete. Total records inserted into PostgreSQL: %d", total_inserted)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    pipeline = IngestionPipeline()
    pipeline.run_all()
