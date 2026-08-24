# Phase-Wise Implementation Plan
## AI-Powered RAG Discovery Engine for Myntra Consumer Behavior

> This document breaks down the full system architecture into **6 sequential phases**, each with clear objectives, deliverables, tasks, dependencies, estimated timelines, and exit criteria. Phases are ordered by dependency — each phase builds on the outputs of the previous one.

---

## Implementation Timeline Overview

```text
Phase 1 ████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  Weeks 1–3
Phase 2 ░░░░░░░░████████░░░░░░░░░░░░░░░░░░░░░░░░░░  Weeks 3–5
Phase 3 ░░░░░░░░░░░░░░░░████████████░░░░░░░░░░░░░░  Weeks 5–8
Phase 4 ░░░░░░░░░░░░░░░░░░░░░░░░░░░░████████░░░░░░  Weeks 8–10
Phase 5 ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██████  Weeks 10–12
Phase 6 ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░████  Weeks 12–14
```

---

## Phase 1 — Project Foundation & Data Collection Infrastructure
**Duration:** Weeks 1–3 · **Architecture Layers:** Layer 1, Layer 2 (partial)

### 1.1 Objective
Stand up the project skeleton, development environment, and all source-specific data scrapers. By end of this phase, raw feedback data from all 6 channels is flowing into a local staging area with a **minimum of 5,000 authentic, unique reviews** collected across all sources (excluding any synthetic or duplicate data).

### 1.2 Tasks

#### 1.2.1 Project Bootstrapping
| # | Task | Details |
| :--- | :--- | :--- |
| 1 | Initialize repository & folder structure | Monorepo with `scrapers/`, `pipeline/`, `nlp/`, `api/`, `dashboard/`, `vectordb/`, `config/`, `tests/` |
| 2 | Set up Python virtual environment | `python 3.11+`, `requirements.txt` / `pyproject.toml` |
| 3 | Configure Docker Compose skeleton | Services: `postgres`, `chromadb`, `redis`, `api` (stubs) |
| 4 | Set up `.env` and secrets management | API keys for Reddit, YouTube, X, Instagram, Play Store |
| 5 | Configure CI pipeline (GitHub Actions) | Lint (`ruff`), type-check (`mypy`), unit tests (`pytest`) on every PR |

#### 1.2.2 Data Source Scrapers
Build one dedicated scraper module per source inside `scrapers/`. **Target: ≥ 5,000 total authentic, unique reviews** across all sources (no synthetic or duplicate data counted):

| # | Scraper | Library / API | Target Volume | Key Implementation Notes |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `scrapers/playstore.py` | `google-play-scraper` | ≥ 1,500 reviews | Paginated fetch, filter by `com.myntra.android`, extract rating + text + date; highest volume source |
| 2 | `scrapers/appstore.py` | `app-store-scraper` | ≥ 800 reviews | Region-aware fetch for Myntra iOS app (India); multi-region if needed |
| 3 | `scrapers/reddit.py` | `PRAW` (Reddit API) | ≥ 1,000 posts+comments | Target subreddits: `r/IndianFashionAddicts`, `r/TwoXIndia`, `r/myntra`; fetch posts + all comments |
| 4 | `scrapers/youtube.py` | YouTube Data API v3 | ≥ 800 comments | Search for Myntra haul/review videos → fetch comment threads; 50+ videos |
| 5 | `scrapers/twitter.py` | `tweepy` / X API v2 | ≥ 500 tweets | Search queries: `"myntra"`, `#myntra`, `@myntra`; fetch tweets + replies |
| 6 | `scrapers/instagram.py` | Instagram Graph API / Instaloader | ≥ 400 posts+comments | Public posts with #myntra; extract captions + comments |

> **Note:** Volume targets are minimums per source. Total across all sources must be **≥ 5,000 unique, authentic records** after deduplication. Synthetic/LLM-generated and duplicate records are excluded from these counts.

#### 1.2.3 Unified Schema & Raw Storage
| # | Task | Details |
| :--- | :--- | :--- |
| 1 | Define unified feedback JSON schema | As per architecture §4.2 — fields: `feedback_id`, `source`, `source_url`, `author_id_hash`, `content_raw`, `timestamp`, `platform_metadata` |
| 2 | Implement source → schema normaliser per scraper | Each scraper outputs records conforming to the unified schema |
| 3 | Raw data staging | Save normalised records to `data/raw/` as JSONL files (one per source per run) |
| 4 | Write unit tests for each scraper | Mock API responses, verify schema output |

### 1.3 Deliverables
- [x] Working scraper for each of the 6 data sources
- [x] Unified feedback schema with normaliser functions
- [x] ≥ 5,000 authentic, unique JSONL raw data records in staging directory
- [x] Docker Compose with PostgreSQL & ChromaDB running
- [x] CI pipeline with linting and unit tests
- [x] Per-source volume report confirming target volumes met

### 1.4 Exit Criteria
✅ Total scraped records across all 6 sources ≥ **5,000 unique, authentic records** (no synthetic/duplicate data).
✅ Per-source minimum met: Play Store ≥ 1,500 · App Store ≥ 800 · Reddit ≥ 1,000 · YouTube ≥ 800 · Twitter ≥ 500 · Instagram ≥ 400.
✅ All records pass unified schema validation (zero schema errors).
✅ Dedup fingerprint check confirms zero exact duplicates in the raw staging output.
✅ `docker compose up` brings up PostgreSQL and ChromaDB without errors.

### 1.5 Risks & Mitigations
| Risk | Mitigation |
| :--- | :--- |
| API rate limits (especially X, Instagram) | Implement exponential backoff + respect rate headers; stagger scrape schedules |
| Instagram Graph API access restrictions | Fall back to public web scraping with Playwright as backup |
| Reddit API deprecations (Pushshift) | Use official PRAW with OAuth; cache aggressively |

---

## Phase 2 — Ingestion Pipeline & Data Quality Gate
**Duration:** Weeks 3–5 · **Architecture Layers:** Layer 2 (complete)

### 2.1 Objective
Build a robust, automated ingestion pipeline that deduplicates, filters synthetic content, and loads clean records into PostgreSQL. By end of this phase, a scheduled pipeline ingests new data daily.

### 2.2 Tasks

#### 2.2.1 PostgreSQL Schema Setup
| # | Task | Details |
| :--- | :--- | :--- |
| 1 | Create `feedback_records` table | Schema as per architecture §6.1 — includes JSONB columns for flexible metadata |
| 2 | Create `topic_clusters` table | `cluster_id`, `cluster_label`, `keywords`, `record_count`, `avg_sentiment` |
| 3 | Create `opportunity_matrix` table | `friction_category`, `friction_label`, `total_mentions`, `frequency_rank`, `opportunity_score` |
| 4 | Create `ingestion_runs` table | Track pipeline run metadata: `run_id`, `source`, `records_fetched`, `records_inserted`, `dedup_dropped`, `synthetic_dropped`, `timestamp` |
| 5 | Write Alembic migrations | Version-controlled schema evolution |

#### 2.2.2 Deduplication Engine
| # | Task | Details |
| :--- | :--- | :--- |
| 1 | Implement exact deduplication | SHA-256 hash of `content_cleaned` → check against `dedup_fingerprint` column |
| 2 | Implement near-deduplication | MinHash LSH with Jaccard threshold ≥ 0.85 using `datasketch` library |
| 3 | Build dedup report | Log counts: total ingested, exact dupes, near dupes, net new records |

#### 2.2.3 Synthetic Data Filter
| # | Task | Details |
| :--- | :--- | :--- |
| 1 | Integrate AI-text detector | Use `binoculars` scoring or GPTZero API to flag suspected LLM-generated reviews |
| 2 | Implement bot filter | Heuristic rules: identical text patterns, posting frequency anomalies |
| 3 | Quarantine mechanism | Flagged records stored in `quarantine_records` table with reason codes; excluded from downstream |

#### 2.2.4 Text Preprocessing
| # | Task | Details |
| :--- | :--- | :--- |
| 1 | Cleaning pipeline | Strip HTML, normalise Unicode, handle emoji, remove URLs (but preserve in metadata) |
| 2 | Language detection | Filter out non-English/non-Hinglish reviews (keep for future multilingual phase) |
| 3 | PII anonymisation | SHA-256 hash author IDs; regex-strip email addresses, phone numbers from content |

#### 2.2.5 Pipeline Orchestration
| # | Task | Details |
| :--- | :--- | :--- |
| 1 | Define Airflow / Prefect DAG | `scrape → normalise → dedup → filter → clean → load` |
| 2 | Schedule daily runs | Cron-based trigger at 02:00 IST daily; event-driven manual trigger for sale periods |
| 3 | Add alerting | Slack/email notification on pipeline failure or anomalous dedup rates |

### 2.3 Deliverables
- [x] PostgreSQL tables created with Alembic migrations
- [x] Deduplication engine (exact + near-dedup) with reporting
- [x] Synthetic data filter with quarantine workflow
- [x] Text preprocessing pipeline
- [x] Scheduled Airflow/Prefect DAG running daily
- [x] Pipeline monitoring dashboard (Airflow UI)

### 2.4 Exit Criteria
✅ Pipeline runs end-to-end on all 6 sources without manual intervention.
✅ Dedup rate is non-trivial (validates that the dedup engine is working).
✅ ≥ **5,000 clean, unique, authentic records** loaded into PostgreSQL (after dedup + synthetic filter).
✅ Zero synthetic/LLM-generated records pass the filter (validated on a known synthetic test set).
✅ Per-source record counts logged and verified against Phase 1 targets.

---

## Phase 3 — NLP Processing & Vector Embedding Pipeline
**Duration:** Weeks 5–8 · **Architecture Layers:** Layer 3, Layer 4

### 3.1 Objective
Enrich every feedback record with structured NLP annotations (sentiment, friction labels, topic clusters, user segments, opportunity scores) and index text chunks as vector embeddings for RAG retrieval.

### 3.2 Tasks

#### 3.2.1 Sentiment & Emotion Analysis
| # | Task | Details |
| :--- | :--- | :--- |
| 1 | Set up sentiment model | Load `cardiffnlp/twitter-roberta-base-sentiment` or fine-tune BERT on fashion domain |
| 2 | Extend beyond pos/neg/neutral | Add emotion dimensions: frustration, delight, confusion, skepticism, urgency |
| 3 | Store results | Write `sentiment_scores` JSONB to `feedback_records` table |
| 4 | Validate accuracy | Manually label 200 records; measure precision/recall |

#### 3.2.2 Intent & Friction Classification
| # | Task | Details |
| :--- | :--- | :--- |
| 1 | Define friction taxonomy | 7 categories, 20+ labels as per architecture §5.2 |
| 2 | Create training dataset | Manually annotate 500+ records across all friction categories |
| 3 | Train multi-label classifier | Fine-tune `distilbert-base-uncased` for multi-label classification |
| 4 | Evaluate model | Macro F1-score ≥ 0.70 on held-out test set |
| 5 | Deploy as inference service | Batch inference on all records; store `friction_labels` JSONB |

#### 3.2.3 Topic & Theme Clustering
| # | Task | Details |
| :--- | :--- | :--- |
| 1 | Run BERTopic | Unsupervised clustering on all `content_cleaned` texts |
| 2 | Label top clusters | Auto-generate + manually review cluster labels and keywords |
| 3 | Store cluster assignments | Write `topic_cluster_id` FK to `feedback_records`; populate `topic_clusters` table |
| 4 | Set up periodic re-clustering | Monthly reclustering to capture emerging themes |

#### 3.2.4 User Segment Tagging
| # | Task | Details |
| :--- | :--- | :--- |
| 1 | Build segment classifiers | Rule-based + ML for 5 segments: Gen Z, Premium, Tier-2/3, Insider, Discount Hunter |
| 2 | Define signal dictionaries | Keyword lists, brand mention lists, behavioral signals per segment |
| 3 | Tag all records | Write `user_segment_tags` JSONB array to `feedback_records` |

#### 3.2.5 Opportunity Scoring
| # | Task | Details |
| :--- | :--- | :--- |
| 1 | Implement scoring formula | `Opportunity Score = f(frequency_rank, estimated_conversion_impact, segment_breadth)` |
| 2 | Compute frequency ranks | Count friction label occurrences across all records |
| 3 | Assign impact weights | Business-logic driven weights mapped to KPIs (conversion, AOV, return rate) |
| 4 | Populate `opportunity_matrix` table | Aggregated view of all friction categories with scores |

#### 3.2.6 Vector Embedding & Indexing
| # | Task | Details |
| :--- | :--- | :--- |
| 1 | Choose embedding model | BGE (`BAAI/bge-large-en-v1.5`, 1024-dim) — open-source, no API cost, high-quality embeddings |
| 2 | Implement chunking strategy | Sentence/paragraph-level chunks with full provenance metadata |
| 3 | Generate embeddings | Batch-embed all chunks via `sentence-transformers` |
| 4 | Load into ChromaDB | Create collection with metadata fields: `feedback_id`, `source`, `source_url`, `friction_labels`, `user_segment` |
| 5 | Build BM25 index | Parallel keyword index using `rank_bm25` for hybrid retrieval |
| 6 | Verify retrieval quality | Manual queries on 20 test questions; verify relevance of top-10 results |

### 3.3 Deliverables
- [x] Sentiment analysis pipeline producing multi-dimensional scores
- [x] Friction classifier (multi-label) with ≥ 0.70 F1-score
- [x] BERTopic clusters with labelled themes
- [x] User segment tags on all records
- [x] Opportunity matrix table fully populated
- [x] ChromaDB collection with all chunks + embeddings + metadata
- [x] BM25 keyword index for hybrid search

### 3.4 Exit Criteria
✅ All `feedback_records` rows (≥ 5,000) have non-null `sentiment_scores`, `friction_labels`, `user_segment_tags`, and `opportunity_score`.
✅ Vector DB contains ≥ **8,000 embedded chunks** with correct metadata (avg ~1.6 chunks per record).
✅ Manual retrieval test: 15/20 test queries return relevant chunks in top-5.

### 3.5 Risks & Mitigations
| Risk | Mitigation |
| :--- | :--- |
| Low friction classifier accuracy | Iteratively expand training set; use active learning on model-uncertain samples |
| Embedding drift across data sources | Normalize text preprocessing per source before embedding |
| BERTopic producing too many micro-clusters | Tune `min_topic_size` and `nr_topics` parameters; merge similar clusters |

---

## Phase 4 — RAG Query Engine & API Backend
**Duration:** Weeks 8–10 · **Architecture Layers:** Layer 5, Layer 7

### 4.1 Objective
Build the complete RAG pipeline — from natural language query input to citation-grounded, synthesized answers — and expose it through a production-ready FastAPI backend.

### 4.2 Tasks

#### 4.2.1 Query Parser & Rewriter
| # | Task | Details |
| :--- | :--- | :--- |
| 1 | Build query intent detector | Classify incoming query into categories: wishlist, friction, segment, comparison, policy, general |
| 2 | Entity extractor | Extract entities: brand names, friction types, segments, date ranges, source platforms |
| 3 | Query rewriter | Expand query with Myntra-domain synonyms (e.g., "size issues" → "fit ambiguity, size chart, true-to-fit") |
| 4 | Metadata filter builder | Convert extracted entities into ChromaDB `where` filters (segment, source, date range) |

#### 4.2.2 Hybrid Retriever
| # | Task | Details |
| :--- | :--- | :--- |
| 1 | Implement vector retrieval | Embed query → cosine similarity search in ChromaDB → top-K chunks |
| 2 | Implement BM25 retrieval | Keyword search on same corpus → top-K results |
| 3 | Reciprocal Rank Fusion (RRF) | Merge vector + BM25 results using RRF scoring; configurable weight ratio |
| 4 | Apply metadata filters | Pre-filter by source, segment, date range before retrieval |
| 5 | Tune retrieval parameters | Optimize `top_k`, RRF weights, similarity thresholds on test query set |

#### 4.2.3 Context Builder & Prompt Engineering
| # | Task | Details |
| :--- | :--- | :--- |
| 1 | Design RAG system prompt | Instruct LLM to synthesize from provided context only; mandate verbatim citations |
| 2 | Chunk assembly | Deduplicate overlapping chunks; order by relevance score |
| 3 | Citation formatting | Each chunk injected with `[Source: {platform}, URL: {url}, Date: {date}]` tags |
| 4 | Context window management | Truncate/prioritize chunks to fit within LLM context limit (8K–128K tokens) |

#### 4.2.4 LLM Generator
| # | Task | Details |
| :--- | :--- | :--- |
| 1 | Integrate LLM provider | Groq API (Llama 3 70B / Mixtral) — ultra-low latency inference |
| 2 | Implement citation contract | Every answer must include: verbatim quote, source platform, URL, date |
| 3 | Hallucination guardrail | If no relevant evidence found, return "Insufficient evidence" response |
| 4 | Confidence scoring | Compute confidence based on retrieval relevance scores and chunk coverage |
| 5 | Response formatter | Structured JSON output: `answer_text`, `citations[]`, `confidence_score`, `related_friction_labels[]` |

#### 4.2.5 FastAPI Backend
| # | Task | Details |
| :--- | :--- | :--- |
| 1 | Scaffold FastAPI app | Project structure: `api/main.py`, `api/routes/`, `api/services/`, `api/models/` |
| 2 | Implement `/api/v1/query` (POST) | RAG query endpoint — accepts natural language, returns cited answer |
| 3 | Implement `/api/v1/feedback` (GET) | Search/filter/paginate raw feedback records |
| 4 | Implement dashboard data endpoints | `opportunity-matrix`, `wishlist-friction`, `segments`, `trends` (GET) |
| 5 | Implement `/api/v1/ingestion/status` (GET) | Pipeline health, last run stats, record counts |
| 6 | Add authentication | API key middleware for programmatic access; JWT for dashboard sessions |
| 7 | Add rate limiting | Per-key limits using `slowapi` to control LLM API costs |
| 8 | Auto-generate OpenAPI docs | FastAPI built-in Swagger UI at `/docs` |
| 9 | Write integration tests | End-to-end tests for each endpoint with mock data |

### 4.3 Deliverables
- [x] Query parser with intent detection, entity extraction, and query rewriting
- [x] Hybrid retriever (vector + BM25 + RRF) with metadata filtering
- [x] RAG pipeline producing citation-grounded answers
- [x] FastAPI backend with all endpoints documented and tested
- [x] Authentication and rate limiting
- [x] OpenAPI docs at `/docs`

### 4.4 Exit Criteria
✅ RAG pipeline answers 20 test queries with relevant, cited responses.
✅ Zero hallucinated citations (all citations verifiable in source data).
✅ API latency: RAG query ≤ 5 seconds (p95); dashboard endpoints ≤ 500ms (p95).
✅ All endpoints return correct HTTP status codes and schema-valid responses.

### 4.5 Risks & Mitigations
| Risk | Mitigation |
| :--- | :--- |
| Groq API rate limits | Cache frequent queries; rate-limit per user; use Groq's generous free tier; fall back to Mixtral for simple queries |
| Hallucinated citations | Enforce strict prompt: "only cite from provided context"; post-generation verification step |
| Slow RAG response time | Pre-filter with metadata before vector search; limit context window; async streaming |

---

## Phase 5 — Interactive Analytics Dashboard
**Duration:** Weeks 10–12 · **Architecture Layers:** Layer 6

### 5.1 Objective
Build a rich, interactive analytics dashboard that consumes the backend APIs and presents visual insights to product managers, category heads, and UX researchers.

### 5.2 Tasks

#### 5.2.1 Frontend Bootstrapping
| # | Task | Details |
| :--- | :--- | :--- |
| 1 | Initialize React app | Vite + React 18 + TypeScript |
| 2 | Set up design system | Color palette, typography (Inter/Outfit), spacing tokens, dark mode support |
| 3 | Install charting libraries | Recharts for standard charts; D3.js for Sankey diagrams; Plotly for heatmaps |
| 4 | Configure API client | Axios instance with base URL, auth headers, error interceptors |

#### 5.2.2 Dashboard Views
| # | View | Components | Data Source (API) |
| :--- | :--- | :--- | :--- |
| 1 | **Opportunity Heatmap** | Interactive heatmap grid (friction × impact); click-to-drill | `/api/v1/dashboard/opportunity-matrix` |
| 2 | **Wishlist vs. Purchase Disconnect** | Sankey diagram (wishlist → outcome by reason); time-series chart with sale event annotations | `/api/v1/dashboard/wishlist-friction` |
| 3 | **Segment Breakdown** | Radar charts per segment; sortable tables with top friction points and representative quotes | `/api/v1/dashboard/segments` |
| 4 | **Trend Timelines** | Rolling line charts (sentiment + volume); spike annotations; date range selector | `/api/v1/dashboard/trends` |
| 5 | **Feedback Explorer** | Searchable, filterable table of raw feedback records with source links | `/api/v1/feedback` |

#### 5.2.3 Embedded RAG Search Bar
| # | Task | Details |
| :--- | :--- | :--- |
| 1 | Build search bar component | Prominent input field with auto-suggest and example queries |
| 2 | Display RAG results | Answer text + expandable citation cards (verbatim quote, source badge, link, date) |
| 3 | Streaming response | SSE/WebSocket for typewriter-style answer rendering |
| 4 | Query history | Sidebar with recent queries for quick re-access |

#### 5.2.4 Interactivity & UX Polish
| # | Task | Details |
| :--- | :--- | :--- |
| 1 | Global filters | Source, segment, date range, friction category, sentiment — applied across all views |
| 2 | Drill-down interactions | Click any heatmap cell / chart segment → modal with underlying feedback records |
| 3 | Export functionality | CSV and PDF export for any view; screenshot-to-clipboard for charts |
| 4 | Responsive layout | Desktop-first (1280px+) with tablet fallback |
| 5 | Loading states & error handling | Skeleton loaders, error boundaries, retry mechanisms |
| 6 | Dark mode | Toggle between light and dark themes |

#### 5.2.5 Frontend Testing
| # | Task | Details |
| :--- | :--- | :--- |
| 1 | Component tests | React Testing Library for all chart and form components |
| 2 | E2E tests | Playwright tests for critical user flows (filter → view → drill-down → export) |
| 3 | Performance audit | Lighthouse score ≥ 90 on Performance and Accessibility |

### 5.3 Deliverables
- [x] Fully functional React dashboard with 5 views + embedded RAG search
- [x] Interactive filters, drill-downs, and export
- [x] Dark mode toggle
- [x] Component and E2E test suites
- [x] Lighthouse audit report

### 5.4 Exit Criteria
✅ All 5 dashboard views render correctly with live API data.
✅ RAG search bar returns cited answers within the dashboard.
✅ Export produces valid CSV/PDF files.
✅ Lighthouse Performance ≥ 90, Accessibility ≥ 90.

---

## Phase 6 — Integration, Testing, Deployment & Documentation
**Duration:** Weeks 12–14 · **Architecture Layers:** All (cross-cutting)

### 6.1 Objective
Integrate all components end-to-end, conduct comprehensive testing, deploy the full system, and produce documentation for handoff and maintainability.

### 6.2 Tasks

#### 6.2.1 End-to-End Integration Testing
| # | Task | Details |
| :--- | :--- | :--- |
| 1 | Full pipeline smoke test | Trigger scraper → ingestion → NLP → storage → verify on dashboard |
| 2 | RAG end-to-end test | Submit query via dashboard → verify answer + citations match source data |
| 3 | Data integrity checks | Verify record counts across PostgreSQL, ChromaDB, and dashboard aggregations |
| 4 | Concurrent load test | Simulate 50 concurrent RAG queries; verify p95 latency ≤ 5s |
| 5 | Edge case testing | Empty query, no results, very long queries, special characters, Hinglish input |

#### 6.2.2 Security & Compliance
| # | Task | Details |
| :--- | :--- | :--- |
| 1 | Security audit | OWASP top-10 review; SQL injection, XSS, CSRF checks |
| 2 | PII audit | Verify zero PII in PostgreSQL and ChromaDB (spot-check 500 records) |
| 3 | API security | Validate auth enforcement on all endpoints; test with expired/invalid tokens |
| 4 | Dependency vulnerability scan | `pip-audit` and `npm audit` on all dependencies |

#### 6.2.3 Monitoring & Observability Setup
| # | Task | Details |
| :--- | :--- | :--- |
| 1 | Pipeline monitoring | Airflow/Prefect dashboards for scraper and ingestion health |
| 2 | API monitoring | Prometheus metrics + Grafana dashboards for request latency, error rates, throughput |
| 3 | RAG quality monitoring | Log every query + answer + citations; periodic manual review of answer quality |
| 4 | Alerting rules | PagerDuty/Slack alerts: pipeline failure, API error rate > 5%, LLM cost spike |

#### 6.2.4 Deployment
| # | Task | Details |
| :--- | :--- | :--- |
| 1 | Finalize `docker-compose.yml` | All services: postgres, chromadb, redis, api, nlp-worker, scraper, dashboard |
| 2 | Write `Dockerfile` per service | Multi-stage builds, minimal images, non-root users |
| 3 | Environment configuration | `.env.production` with all API keys, DB URLs, LLM provider keys |
| 4 | Deploy to staging | Docker Compose on a cloud VM (AWS EC2 / GCP Compute) |
| 5 | Staging validation | Run full test suite against staging environment |
| 6 | Deploy to production | Production deployment with proper resource limits and health checks |
| 7 | DNS & SSL | Configure domain, HTTPS via Let's Encrypt / Cloudflare |

#### 6.2.5 Documentation
| # | Document | Contents |
| :--- | :--- | :--- |
| 1 | `README.md` | Project overview, quick start, architecture summary |
| 2 | `docs/setup.md` | Development environment setup, dependency installation, environment variables |
| 3 | `docs/api_reference.md` | All API endpoints with request/response examples |
| 4 | `docs/data_pipeline.md` | Scraper configuration, ingestion DAG, scheduling, monitoring |
| 5 | `docs/nlp_models.md` | Model cards for sentiment, friction classifier, BERTopic; retraining instructions |
| 6 | `docs/rag_engine.md` | RAG pipeline architecture, prompt templates, retrieval tuning guide |
| 7 | `docs/dashboard_guide.md` | User guide for dashboard views, filters, RAG search, export |
| 8 | `docs/deployment.md` | Docker deployment, environment config, scaling guide |
| 9 | `docs/runbook.md` | Operational runbook: common failure modes, troubleshooting steps, recovery procedures |

### 6.3 Deliverables
- [x] All integration and E2E tests passing
- [x] Security and PII audits completed with zero critical findings
- [x] Monitoring dashboards and alerting configured
- [x] Production deployment live and accessible
- [x] Full documentation suite

### 6.4 Exit Criteria
✅ End-to-end smoke test passes: scraper → dashboard + RAG query — all correct.
✅ Zero critical security findings.
✅ Production system stable for 48 hours with no unhandled errors.
✅ All documentation reviewed and approved by team.

---

## Phase Dependency Map

```text
Phase 1                    Phase 2                    Phase 3
Project Foundation  ──────► Ingestion Pipeline  ──────► NLP & Vector
& Data Collection           & Data Quality              Embedding Pipeline
                                                              │
                                                    ┌─────────┴─────────┐
                                                    ▼                   ▼
                                              Phase 4              Phase 5
                                              RAG Engine           Analytics
                                              & API Backend        Dashboard
                                                    │                   │
                                                    └─────────┬─────────┘
                                                              ▼
                                                        Phase 6
                                                        Integration,
                                                        Testing &
                                                        Deployment
```

---

## Resource & Cost Estimates

### Compute
| Resource | Estimated Monthly Cost | Notes |
| :--- | :--- | :--- |
| Cloud VM (API + Workers) | $80–150 | 4 vCPU, 16GB RAM, SSD |
| PostgreSQL (managed) | $25–50 | Small instance, ~10GB data |
| Vector DB (Qdrant Cloud / Pinecone) | $0–70 | Free tier for dev; paid for prod scale |
| LLM API (Groq) | $0–50 | Groq offers generous free tier; paid tier is significantly cheaper than OpenAI |

### Team Effort
| Role | Estimated Effort |
| :--- | :--- |
| **Backend / Data Engineer** | 8–10 weeks (Phases 1–4, 6) |
| **ML / NLP Engineer** | 4–5 weeks (Phase 3, partial Phase 4) |
| **Frontend Engineer** | 3–4 weeks (Phase 5, partial Phase 6) |
| **Total** | ~14 weeks (3.5 months) for a 2–3 person team |

---

## Summary — Phase Quick Reference

| Phase | Focus | Weeks | Key Output |
| :--- | :--- | :--- | :--- |
| **Phase 1** | Foundation & Data Collection | 1–3 | 6 working scrapers, ≥ 5,000 authentic reviews, unified schema, Docker environment |
| **Phase 2** | Ingestion Pipeline & Quality Gate | 3–5 | Automated daily pipeline, dedup, synthetic filter, ≥ 5,000 clean records in PostgreSQL |
| **Phase 3** | NLP Processing & Embeddings | 5–8 | Sentiment, friction, segments, opportunity scores, ≥ 8,000 chunks in ChromaDB |
| **Phase 4** | RAG Engine & API Backend | 8–10 | Citation-grounded RAG, FastAPI with all endpoints |
| **Phase 5** | Analytics Dashboard | 10–12 | React dashboard with 5 views + embedded RAG search |
| **Phase 6** | Integration, Deploy & Docs | 12–14 | Production deployment, monitoring, full documentation |
