"""
Standalone script to ingest raw JSONL data directly into ChromaDB.

This bypasses the full IngestionPipeline (which requires PostgreSQL)
and directly indexes cleaned + analyzed feedback into ChromaDB for RAG queries.

Usage:
    python ingest_to_chroma.py
"""

import json
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from nlp.cleaner import TextCleaner
from nlp.analyzer import NLPAnalyzer
from vectordb.indexer import VectorIndexer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def ingest_raw_data(data_dir: str = "data/raw", max_records: int = 200) -> None:
    """
    Read raw JSONL files, clean, analyze sentiment, and index into ChromaDB.
    
    Args:
        data_dir: Path to raw JSONL directory
        max_records: Max records to process (to keep indexing fast)
    """
    data_path = Path(data_dir)
    jsonl_files = list(data_path.glob("*.jsonl"))
    
    if not jsonl_files:
        logger.error("No JSONL files found in %s", data_dir)
        return
    
    logger.info("Found %d JSONL file(s) to process", len(jsonl_files))
    
    # Initialize components
    logger.info("Initializing NLP components...")
    cleaner = TextCleaner()
    analyzer = NLPAnalyzer(device=-1)  # CPU
    
    logger.info("Connecting to ChromaDB...")
    indexer = VectorIndexer(host="localhost", port=8000)
    
    total_indexed = 0
    total_skipped = 0
    
    for file_path in jsonl_files:
        logger.info("Processing: %s", file_path.name)
        
        records_in_file = 0
        
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                
                if total_indexed >= max_records:
                    logger.info("Reached max_records limit (%d). Stopping.", max_records)
                    break
                
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    total_skipped += 1
                    continue
                
                raw_text = record.get("content_raw", "")
                if not raw_text or len(raw_text.strip()) < 10:
                    total_skipped += 1
                    continue
                
                # 1. Clean
                clean_result = cleaner.process_record(raw_text)
                if not clean_result["is_supported_language"]:
                    total_skipped += 1
                    continue
                
                cleaned_text = clean_result["content_cleaned"]
                if len(cleaned_text.strip()) < 10:
                    total_skipped += 1
                    continue
                
                # 2. Analyze sentiment & frictions
                enriched = analyzer.enrich_record(cleaned_text)
                
                # 3. Build record for indexer
                index_record = {
                    "feedback_id": record.get("feedback_id", f"rec_{total_indexed}"),
                    "content_cleaned": cleaned_text,
                    "source": record.get("source", "unknown"),
                    "source_url": record.get("source_url", ""),
                    "author_id_hash": record.get("author_id_hash", ""),
                    "timestamp": record.get("timestamp", ""),
                    "sentiment": enriched.get("sentiment", {"label": "neutral"}),
                    "frictions": enriched.get("frictions", []),
                    "segments": enriched.get("segments", []),
                }
                
                # 4. Index into ChromaDB
                indexer.index_record(index_record)
                total_indexed += 1
                records_in_file += 1
                
                if total_indexed % 50 == 0:
                    logger.info("Progress: %d records indexed...", total_indexed)
                    
            else:
                # Inner loop completed normally (no break)
                logger.info("Finished file %s: %d records indexed", file_path.name, records_in_file)
                continue
            
            # Break out of outer loop if max hit
            logger.info("Finished file %s: %d records indexed", file_path.name, records_in_file)
            break
    
    logger.info("=" * 60)
    logger.info("Ingestion complete!")
    logger.info("  Total indexed:  %d", total_indexed)
    logger.info("  Total skipped:  %d", total_skipped)
    logger.info("=" * 60)
    
    # Verify
    count = indexer.collection.count()
    logger.info("ChromaDB collection '%s' now has %d chunks.", indexer.collection.name, count)


if __name__ == "__main__":
    ingest_raw_data(max_records=200)
