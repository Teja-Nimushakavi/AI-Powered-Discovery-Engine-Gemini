"""
CLI Entry Point — Run scrapers for the RAG Discovery Engine.

Usage:
    python run_scrapers.py --all                     # Run all 6 scrapers
    python run_scrapers.py --source reddit            # Run a specific scraper
    python run_scrapers.py --source playstore --max 500  # Custom max records
    python run_scrapers.py --report                   # Show volume report

Target: ≥ 5,000 total authentic, unique reviews across all sources.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from rich.logging import RichHandler

from config.settings import get_settings
from models.schema import SourceEnum

console = Console()

# Per-source minimum targets
SOURCE_TARGETS: dict[str, int] = {
    "playstore": 1500,
    "appstore": 800,
    "reddit": 1000,
    "youtube": 800,
    "twitter": 500,
    "instagram": 400,
}

TOTAL_TARGET = 5000


def setup_logging(level: str = "INFO") -> None:
    """Configure logging with Rich handler for pretty console output."""
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True)],
    )


def get_scraper(source: str, max_records: int | None = None):  # type: ignore[no-untyped-def]
    """
    Factory function to create a scraper instance by source name.
    
    Args:
        source: Source name (playstore, appstore, reddit, youtube, twitter, instagram)
        max_records: Maximum records to fetch (overrides source default)
    
    Returns:
        An instance of the appropriate scraper class.
    """
    if source == "playstore":
        from scrapers.playstore import PlayStoreScraper
        return PlayStoreScraper(max_records=max_records)
    elif source == "appstore":
        from scrapers.appstore import AppStoreScraper
        return AppStoreScraper(max_records=max_records)
    elif source == "reddit":
        from scrapers.reddit import RedditScraper
        return RedditScraper(max_records=max_records)
    elif source == "youtube":
        from scrapers.youtube import YouTubeScraper
        return YouTubeScraper(max_records=max_records)
    elif source == "twitter":
        from scrapers.twitter import TwitterScraper
        return TwitterScraper(max_records=max_records)
    elif source == "instagram":
        from scrapers.instagram import InstagramScraper
        return InstagramScraper(max_records=max_records)
    else:
        raise ValueError(f"Unknown source: {source}. Valid: {list(SOURCE_TARGETS.keys())}")


def count_existing_records(data_dir: Path) -> dict[str, int]:
    """Count existing records per source from JSONL files in data/raw/."""
    counts: dict[str, int] = {source: 0 for source in SOURCE_TARGETS}

    if not data_dir.exists():
        return counts

    for jsonl_file in data_dir.glob("*.jsonl"):
        # Filename format: {source}_{timestamp}.jsonl
        source_name = jsonl_file.stem.rsplit("_", 2)[0]
        if source_name in counts:
            with open(jsonl_file, "r", encoding="utf-8") as f:
                for _ in f:
                    counts[source_name] += 1

    return counts


def print_volume_report(counts: dict[str, int]) -> None:
    """Print a rich table showing scraper volume vs targets."""
    table = Table(
        title="📊 Scraper Volume Report",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Source", style="cyan", min_width=12)
    table.add_column("Target", justify="right", style="yellow")
    table.add_column("Collected", justify="right", style="green")
    table.add_column("Status", justify="center")
    table.add_column("% Complete", justify="right")

    total_collected = 0
    for source, target in SOURCE_TARGETS.items():
        collected = counts.get(source, 0)
        total_collected += collected
        pct = (collected / target * 100) if target > 0 else 0
        status = "✅" if collected >= target else "❌"
        table.add_row(
            source.title(),
            str(target),
            str(collected),
            status,
            f"{pct:.0f}%",
        )

    table.add_section()
    total_pct = (total_collected / TOTAL_TARGET * 100) if TOTAL_TARGET > 0 else 0
    total_status = "✅" if total_collected >= TOTAL_TARGET else "❌"
    table.add_row(
        "TOTAL",
        str(TOTAL_TARGET),
        str(total_collected),
        total_status,
        f"{total_pct:.0f}%",
        style="bold",
    )

    console.print()
    console.print(table)
    console.print()


@click.command()
@click.option(
    "--source", "-s",
    type=click.Choice(list(SOURCE_TARGETS.keys()), case_sensitive=False),
    help="Run a specific scraper (omit to use --all)",
)
@click.option(
    "--all", "run_all",
    is_flag=True,
    default=False,
    help="Run all 6 scrapers",
)
@click.option(
    "--max", "max_records",
    type=int,
    default=None,
    help="Override max records to fetch per scraper",
)
@click.option(
    "--report",
    is_flag=True,
    default=False,
    help="Show volume report for existing scraped data",
)
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    default="INFO",
    help="Logging level",
)
def main(
    source: str | None,
    run_all: bool,
    max_records: int | None,
    report: bool,
    log_level: str,
) -> None:
    """
    🔍 RAG Discovery Engine — Data Scraper CLI

    Scrape authentic Myntra feedback from 6 data sources.
    Target: ≥ 5,000 unique reviews across all sources.
    """
    setup_logging(log_level)
    settings = get_settings()

    if report:
        counts = count_existing_records(settings.raw_data_path)
        print_volume_report(counts)
        return

    if not source and not run_all:
        console.print(
            "[yellow]⚠️  Specify --source <name> or --all to run scrapers.[/yellow]"
        )
        console.print("Available sources:", ", ".join(SOURCE_TARGETS.keys()))
        console.print("\nRun with --help for usage information.")
        sys.exit(1)

    sources_to_run = list(SOURCE_TARGETS.keys()) if run_all else [source]  # type: ignore[list-item]

    console.print(f"\n[bold cyan]🚀 Starting scraper(s): {', '.join(sources_to_run)}[/bold cyan]\n")

    results: dict[str, int] = {}

    for src in sources_to_run:
        console.rule(f"[bold]{src.upper()} Scraper")

        try:
            scraper = get_scraper(src, max_records=max_records)
            records = scraper.run()
            results[src] = len(records)
            console.print(
                f"[green]✅ {src}: {len(records)} records scraped and saved[/green]\n"
            )
        except Exception as e:
            results[src] = 0
            console.print(f"[red]❌ {src}: Failed — {e}[/red]\n")
            logging.getLogger(__name__).exception("Scraper failed for %s", src)

    # Final report
    console.rule("[bold]Scraper Run Summary")
    counts = count_existing_records(settings.raw_data_path)
    # Merge current run results
    for src, count in results.items():
        counts[src] = counts.get(src, 0)  # Already saved to JSONL
    print_volume_report(counts)


if __name__ == "__main__":
    main()
