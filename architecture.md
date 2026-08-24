# Architecture: AI-Powered RAG Discovery Engine for Myntra Consumer Behavior

## Table of Contents
1. [Architecture Overview](#1-architecture-overview)
2. [High-Level System Diagram](#2-high-level-system-diagram)
3. [Layer 1 — Data Sources & Collection](#3-layer-1--data-sources--collection)
4. [Layer 2 — Ingestion Pipeline](#4-layer-2--ingestion-pipeline)
5. [Layer 3 — NLP Processing & Feature Extraction](#5-layer-3--nlp-processing--feature-extraction)
6. [Layer 4 — Storage & Indexing](#6-layer-4--storage--indexing)
7. [Layer 5 — RAG Query Engine](#7-layer-5--rag-query-engine)
8. [Layer 6 — Interactive Analytics Dashboard](#8-layer-6--interactive-analytics-dashboard)
9. [Layer 7 — API & Backend Services](#9-layer-7--api--backend-services)
10. [Cross-Cutting Concerns](#10-cross-cutting-concerns)
11. [Technology Stack Summary](#11-technology-stack-summary)
12. [Data Flow — End-to-End Walkthrough](#12-data-flow--end-to-end-walkthrough)
13. [Deployment Architecture](#13-deployment-architecture)
14. [Future Extensibility](#14-future-extensibility)

---

## 1. Architecture Overview

The system is designed as a **modular, layered pipeline** that transforms raw, unstructured consumer discourse from multiple public channels into structured, queryable intelligence. It is built around two primary consumer-facing outputs:

1. **Interactive Analytics Dashboard** — Visual, quantified friction-point analysis.
2. **RAG-Based Conversational Query Engine** — Natural language search grounded in authentic, cited user feedback.

### Design Principles
| Principle | Description |
| :--- | :--- |
| **Authenticity-First** | Zero synthetic or LLM-generated data enters the pipeline. Every insight is traceable to a real user utterance. |
| **Modular Layers** | Each processing stage is independently deployable and testable. |
| **Citation-Grounded RAG** | Every generated answer must include verbatim source citations. |
| **Myntra-Domain Focus** | All models, taxonomies, and heuristics are tuned to fashion e-commerce behavior on the Myntra platform. |
| **Scalability** | Designed to handle millions of feedback records and concurrent queries. |

---

## 2. High-Level System Diagram

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                              DATA SOURCES (Layer 1)                              │
│  ┌──────────────┐ ┌──────────┐ ┌─────────────────┐ ┌─────────┐ ┌────────────┐  │
│  │ Play / App   │ │  Reddit  │ │ YouTube Comments │ │ X (Twitter)│ │ Instagram │  │
│  │ Store Reviews │ │ Threads  │ │  on Haul Videos  │ │  Posts   │ │  Posts     │  │
│  └──────┬───────┘ └────┬─────┘ └───────┬──────────┘ └────┬────┘ └─────┬──────┘  │
│         │              │               │                  │            │          │
└─────────┼──────────────┼───────────────┼──────────────────┼────────────┼──────────┘
          └──────────────┴───────┬───────┴──────────────────┴────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                          INGESTION PIPELINE (Layer 2)                            │
│  ┌─────────────────┐  ┌──────────────────┐  ┌────────────────────────────────┐  │
│  │ Source-Specific  │→ │ Normalisation &  │→ │ Strict Deduplication &         │  │
│  │ Scrapers / APIs  │  │ Schema Mapping   │  │ Synthetic Data Filter          │  │
│  └─────────────────┘  └──────────────────┘  └────────────────────────────────┘  │
└────────────────────────────────────┬─────────────────────────────────────────────┘
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                     NLP PROCESSING & EXTRACTION (Layer 3)                        │
│  ┌──────────────┐  ┌──────────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │ Sentiment &  │  │ Intent & Friction│  │ Topic / Theme│  │ User Segment   │  │
│  │ Emotion      │  │ Classification   │  │ Clustering   │  │ Tagging        │  │
│  └──────────────┘  └──────────────────┘  └──────────────┘  └────────────────┘  │
└────────────────────────────────────┬─────────────────────────────────────────────┘
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                       STORAGE & INDEXING (Layer 4)                               │
│  ┌──────────────────────┐         ┌──────────────────────────────────────────┐  │
│  │ Structured Database  │         │ Vector Database                          │  │
│  │ (PostgreSQL / MySQL) │         │ (ChromaDB / Pinecone / Qdrant)           │  │
│  │ — metadata, tags,    │         │ — semantic embeddings of every feedback  │  │
│  │   scores, segments   │         │   chunk with source provenance           │  │
│  └──────────┬───────────┘         └──────────────────┬───────────────────────┘  │
└─────────────┼────────────────────────────────────────┼──────────────────────────┘
              │                                        │
              ▼                                        ▼
┌─────────────────────────────┐    ┌──────────────────────────────────────────────┐
│  ANALYTICS DASHBOARD        │    │  RAG QUERY ENGINE (Layer 5)                  │
│  (Layer 6)                  │    │  ┌────────────┐  ┌───────────┐  ┌─────────┐ │
│  ┌────────────────────────┐ │    │  │ Query      │→ │ Retriever │→ │ LLM     │ │
│  │ Opportunity Heatmaps   │ │    │  │ Parser &   │  │ (Vector   │  │ Answer  │ │
│  │ Wishlist Friction      │ │    │  │ Rewriter   │  │  Search)  │  │ + Cite  │ │
│  │ Segment Insights       │ │    │  └────────────┘  └───────────┘  └─────────┘ │
│  │ Trend Timelines        │ │    └──────────────────────────────────────────────┘
│  └────────────────────────┘ │
└─────────────────────────────┘
```

---

## 3. Layer 1 — Data Sources & Collection

All data must be **authentic, publicly available user-generated content**. No synthetic or LLM-generated data is permitted at any stage. **Minimum target: ≥ 5,000 unique, authentic records** across all sources after deduplication.

### 3.1 Source Inventory

| Source | Content Type | Collection Method | Target Volume | Key Signals |
| :--- | :--- | :--- | :--- | :--- |
| **Google Play Store** | App reviews & ratings | Play Store Scraper API / `google-play-scraper` | ≥ 1,500 | Star ratings, review text, review date, device info |
| **Apple App Store** | App reviews & ratings | App Store Scraper / `app-store-scraper` | ≥ 800 | Star ratings, review text, version, region |
| **Reddit** | Posts & comments from r/IndianFashionAddicts, r/TwoXIndia, r/myntra | Reddit API (PRAW) / Pushshift | ≥ 1,000 | Thread title, body, comments, upvotes, subreddit |
| **YouTube** | Comments on try-on hauls & review videos | YouTube Data API v3 | ≥ 800 | Comment text, likes, replies, video context |
| **X (Twitter)** | Public tweets & replies mentioning Myntra | X API v2 (Academic/Basic) | ≥ 500 | Tweet text, engagement, hashtags, mentions |
| **Instagram** | Public post captions & comments | Instagram Graph API / Instaloader | ≥ 400 | Caption text, comments, hashtags, engagement |

> **Total minimum: ≥ 5,000 unique, authentic records.** Synthetic/LLM-generated content and exact/near-duplicates are excluded from all volume counts.

### 3.2 Collection Frequency
- **App Store Reviews:** Daily incremental scraping.
- **Reddit / YouTube / X / Instagram:** Scheduled batch collection every 6–12 hours, with event-driven spikes around major sales (EORS, Big Fashion Festival).

---

## 4. Layer 2 — Ingestion Pipeline

### 4.1 Source-Specific Scrapers
Each data source has a dedicated scraper/connector module responsible for:
- Authenticating with the source API.
- Paginating through results.
- Extracting raw records in source-native format.

### 4.2 Normalisation & Schema Mapping
All raw records are transformed into a **unified feedback schema**:

```json
{
  "feedback_id": "uuid-v4",
  "source": "reddit | playstore | appstore | youtube | twitter | instagram",
  "source_url": "https://...",
  "author_id_hash": "sha256-anonymised",
  "content_raw": "Original user text...",
  "content_cleaned": "Preprocessed text...",
  "timestamp": "ISO-8601",
  "platform_metadata": {
    "rating": 4,
    "subreddit": "IndianFashionAddicts",
    "upvotes": 23
  },
  "ingestion_timestamp": "ISO-8601",
  "dedup_fingerprint": "sha256-of-cleaned-content"
}
```

### 4.3 Strict Deduplication & Synthetic Data Filter
| Step | Method | Purpose |
| :--- | :--- | :--- |
| **Exact Dedup** | SHA-256 hash of cleaned content | Eliminate identical cross-posted reviews |
| **Near-Dedup** | MinHash LSH (Jaccard similarity ≥ 0.85) | Catch paraphrased duplicates |
| **Synthetic Filter** | LLM-generated text detector (e.g., GPTZero / Binoculars score) | Flag and quarantine suspected AI-generated reviews |
| **Bot Filter** | Heuristic rules (post frequency, pattern repetition) | Remove bot-generated spam |

> **Data Authenticity Gate:** Any record flagged by the Synthetic Filter is quarantined and excluded from downstream processing. Manual review queue available for borderline cases. Synthetic and duplicate records are **never** counted toward the 5,000-record minimum. Only verified authentic, unique records pass through to NLP processing and storage.

---

## 5. Layer 3 — NLP Processing & Feature Extraction

This layer enriches every feedback record with structured annotations aligned to the **Core Investigative Pillars** defined in the problem statement.

### 5.1 Sentiment & Emotion Analysis
- **Model:** Fine-tuned transformer (e.g., `cardiffnlp/twitter-roberta-base-sentiment` or domain-adapted BERT).
- **Output:** Multi-dimensional sentiment (not just pos/neg/neutral) — captures frustration, delight, confusion, skepticism, urgency.

### 5.2 Intent & Friction Classification
A multi-label classifier trained on Myntra-specific friction taxonomies:

| Friction Category | Example Labels |
| :--- | :--- |
| **Wishlist Behavior** | `passive_curation`, `price_wait`, `size_unavailable`, `gift_idea` |
| **Sizing & Fit** | `fit_ambiguity`, `size_chart_distrust`, `model_vs_reality` |
| **Visual Accuracy** | `color_mismatch`, `fabric_opacity`, `studio_lighting_gap` |
| **Pricing & Value** | `price_drop_wait`, `coupon_dependency`, `competitor_cheaper` |
| **Policy & Trust** | `return_fee_friction`, `exchange_window_short`, `refund_delay` |
| **External Validation** | `seeks_youtube_review`, `checks_reddit`, `instagram_try_on` |
| **Comparative Shopping** | `brand_comparison`, `private_label_vs_branded`, `multi_platform_check` |

### 5.3 Topic & Theme Clustering
- **Method:** BERTopic or Top2Vec for unsupervised discovery of emerging themes.
- **Purpose:** Surface new friction patterns not covered by the predefined taxonomy.

### 5.4 User Segment Tagging
Heuristic and model-based tagging to classify feedback authors into shopper segments:

| Segment | Signals |
| :--- | :--- |
| **Gen Z / Myntra FWD** | Subreddit context, language patterns, brand mentions (streetwear, sneakers) |
| **Premium / Occasion Buyer** | High-value brand mentions, wedding/festive keywords |
| **Tier-2/3 Consumer** | References to delivery time, COD preference, local brand familiarity |
| **Myntra Insider (Loyal)** | Mentions of insider points, loyalty tiers, repeat purchase history |
| **Price-Sensitive / Discount Hunter** | Sale-wait behavior, coupon mentions, EORS/BFF references |

### 5.5 Opportunity Scoring
Each friction instance is scored on two axes:
- **Frequency:** How often this friction appears across all feedback.
- **Estimated Impact:** Mapped to business KPIs (conversion lift potential, AOV impact, return rate reduction).

```text
Opportunity Score = f(frequency_rank, estimated_conversion_impact, segment_breadth)
```

---

## 6. Layer 4 — Storage & Indexing

### 6.1 Structured Database (PostgreSQL)
Stores all processed metadata, annotations, scores, and aggregations:

```text
┌─────────────────────────────────────────────────┐
│  feedback_records                                │
│  ─────────────────                               │
│  feedback_id (PK)                                │
│  source, source_url, author_id_hash              │
│  content_raw, content_cleaned                    │
│  timestamp, ingestion_timestamp                  │
│  sentiment_scores (JSONB)                        │
│  friction_labels (JSONB)                         │
│  topic_cluster_id (FK)                           │
│  user_segment_tags (JSONB)                       │
│  opportunity_score (FLOAT)                       │
│  dedup_fingerprint                               │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  topic_clusters                                  │
│  ──────────────                                  │
│  cluster_id (PK)                                 │
│  cluster_label, keywords                         │
│  record_count, avg_sentiment                     │
│  first_seen, last_seen                           │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  opportunity_matrix                              │
│  ──────────────────                              │
│  friction_category, friction_label               │
│  total_mentions, frequency_rank                  │
│  estimated_conversion_impact                     │
│  affected_segments (JSONB)                       │
│  opportunity_score                               │
│  last_computed                                   │
└─────────────────────────────────────────────────┘
```

### 6.2 Vector Database (ChromaDB / Pinecone / Qdrant)
Stores semantic embeddings for RAG retrieval:

| Field | Description |
| :--- | :--- |
| `embedding` | Dense vector (1024-dim) from BGE embedding model (`BAAI/bge-large-en-v1.5`) |
| `feedback_id` | Foreign key back to structured DB |
| `content_chunk` | The original text chunk (for verbatim citation) |
| `source` | Platform origin |
| `source_url` | Direct link to original post/review |
| `friction_labels` | Pre-computed friction tags (for filtered retrieval) |
| `user_segment` | Segment tag (for segment-scoped queries) |

### 6.3 Chunking Strategy
- Feedback records are chunked at the **sentence or paragraph level** to preserve citation granularity.
- Each chunk retains full provenance metadata (source, URL, author hash, timestamp).

---

## 7. Layer 5 — RAG Query Engine

### 7.1 Architecture

```text
  User Query (Natural Language)
          │
          ▼
  ┌───────────────────┐
  │  Query Parser &   │  — Intent detection, entity extraction
  │  Rewriter         │  — Expands query with Myntra-domain synonyms
  └────────┬──────────┘
           │
           ▼
  ┌───────────────────┐
  │  Hybrid Retriever │  — Semantic search (vector similarity)
  │                   │  — Keyword search (BM25) for exact terms
  │                   │  — Metadata filters (segment, source, date)
  └────────┬──────────┘
           │  Top-K relevant chunks (with provenance)
           ▼
  ┌───────────────────┐
  │  Context Builder  │  — Assembles retrieved chunks into prompt context
  │                   │  — Deduplicates overlapping chunks
  │                   │  — Enforces citation formatting
  └────────┬──────────┘
           │
           ▼
  ┌───────────────────┐
  │  LLM Generator    │  — Synthesizes answer from retrieved context
  │  (Groq — Llama 3  │  — Includes verbatim citations with source links
  │   via Groq API)    │  — Refuses to answer if no relevant evidence found
  └────────┬──────────┘
           │
           ▼
  ┌───────────────────┐
  │  Response         │  — Structured JSON response with:
  │  Formatter        │     • answer_text
  │                   │     • citations[] (text, source, url, date)
  │                   │     • confidence_score
  │                   │     • related_friction_labels[]
  └───────────────────┘
```

### 7.2 Query Examples

| User Query | Expected Behavior |
| :--- | :--- |
| *"Why do people add to wishlist but don't buy?"* | Retrieves chunks tagged `passive_curation`, `price_wait`; synthesizes top reasons with citations |
| *"What sizing issues do Gen Z shoppers face?"* | Filters by segment `gen_z`, retrieves `fit_ambiguity` chunks; cites specific complaints |
| *"How did the new return fee affect purchase decisions?"* | Filters by `return_fee_friction`; surfaces before/after sentiment shift with user quotes |
| *"What do Reddit users say about Roadster vs HRX quality?"* | Filters source=`reddit`, retrieves `brand_comparison` chunks for both brands |

### 7.3 Citation Contract
Every RAG response **must** include:
- The **verbatim user quote** used as evidence.
- The **source platform** (e.g., Reddit, Play Store).
- A **direct link** to the original post/review where possible.
- The **date** of the original feedback.

---

## 8. Layer 6 — Interactive Analytics Dashboard

### 8.1 Dashboard Views

#### Opportunity Heatmap
A matrix visualization ranking friction categories by frequency × estimated impact. Color-coded cells indicate urgency.

```text
                     Low Impact ◄────────────► High Impact
   High Frequency  │  ██ Sizing    │  ██ Return Fee  │
                   │  Confusion    │  Friction       │
   ───────────────┼───────────────┼─────────────────│
   Low Frequency   │  ░░ Color     │  ░░ COD         │
                   │  Mismatch    │  Demand         │
```

#### Wishlist vs. Purchase Disconnect
- Sankey diagram showing flow from wishlist-add → purchase / abandon, broken down by friction reason.
- Time-series of wishlist-to-purchase conversion rate correlated with sale events.

#### Segment Breakdown
- Radar charts comparing friction profiles across shopper segments.
- Drill-down tables with per-segment top friction points and representative quotes.

#### Trend Timelines
- Rolling sentiment and friction-category volume over time.
- Spike detection annotated with external events (sales, policy changes, viral social media posts).

### 8.2 Interactivity Features
- **Filters:** Source, segment, date range, friction category, sentiment.
- **Drill-down:** Click any data point to see underlying feedback records with source links.
- **Export:** CSV / PDF export of any view for stakeholder reporting.
- **Embedded RAG Search:** Query bar integrated directly into the dashboard for ad-hoc exploration.

---

## 9. Layer 7 — API & Backend Services

### 9.1 API Endpoints

| Endpoint | Method | Purpose |
| :--- | :--- | :--- |
| `/api/v1/query` | `POST` | Submit natural language query to RAG engine |
| `/api/v1/dashboard/opportunity-matrix` | `GET` | Retrieve opportunity matrix data |
| `/api/v1/dashboard/wishlist-friction` | `GET` | Retrieve wishlist disconnect analysis |
| `/api/v1/dashboard/segments` | `GET` | Retrieve segment breakdown data |
| `/api/v1/dashboard/trends` | `GET` | Retrieve time-series trend data |
| `/api/v1/feedback` | `GET` | Search/filter raw feedback records |
| `/api/v1/ingestion/status` | `GET` | Pipeline health and ingestion stats |

### 9.2 Backend Framework
- **Framework:** FastAPI (Python) — async, high-performance, auto-generated OpenAPI docs.
- **Authentication:** API key-based for internal teams; JWT for dashboard sessions.
- **Rate Limiting:** Per-user query rate limits to manage LLM API costs.

---

## 10. Cross-Cutting Concerns

### 10.1 Data Privacy & Compliance
- All author identifiers are **SHA-256 hashed** before storage — no PII is retained.
- Only **publicly accessible** content is ingested; no private messages or gated content.
- Compliance with platform Terms of Service for each data source.

### 10.2 Monitoring & Observability
- **Pipeline Monitoring:** Ingestion success/failure rates, dedup hit rates, processing latency.
- **RAG Quality Monitoring:** Answer relevance scoring, citation accuracy checks, hallucination detection.
- **Dashboard Metrics:** Query volume, most-queried friction categories, user engagement.

### 10.3 Data Freshness
- Target: Feedback records available for querying within **12 hours** of publication on source platform.
- Dashboard aggregations recomputed on a **daily cadence**.

---

## 11. Technology Stack Summary

| Layer | Technology | Rationale |
| :--- | :--- | :--- |
| **Scrapers / Connectors** | Python (`PRAW`, `google-play-scraper`, `youtube-api`, `tweepy`) | Mature libraries for each platform |
| **Ingestion Orchestration** | Apache Airflow / Prefect | Scheduled DAGs, retry logic, monitoring |
| **NLP / ML** | Hugging Face Transformers, spaCy, BERTopic | State-of-the-art NLP with domain fine-tuning |
| **Embeddings** | BGE (`BAAI/bge-large-en-v1.5`) via `sentence-transformers` | Open-source, high-quality 1024-dim dense vectors; no API cost |
| **Vector Database** | ChromaDB (dev) / Pinecone or Qdrant (prod) | Fast approximate nearest neighbor search |
| **Structured Database** | PostgreSQL (with JSONB) | Robust, extensible relational storage |
| **Backend API** | FastAPI (Python) | Async, auto-docs, high performance |
| **LLM for RAG** | Groq (Llama 3 70B / Mixtral via Groq API) | Ultra-low latency inference; generous free tier |
| **Dashboard Frontend** | React + Recharts / D3.js / Plotly | Interactive, component-based visualizations |
| **Deployment** | Docker + Docker Compose (dev) / Kubernetes (prod) | Containerised, scalable microservices |
| **CI/CD** | GitHub Actions | Automated testing and deployment |

---

## 12. Data Flow — End-to-End Walkthrough

```text
1. COLLECT     Scrapers pull new reviews/posts/comments from all 6 sources
                                          │
2. NORMALISE   Raw records → unified feedback schema (JSON)
                                          │
3. DEDUP       Exact + near-duplicate removal; synthetic data quarantine
                                          │
4. ENRICH      NLP pipeline tags each record with:
               sentiment, friction labels, topic cluster, user segment, opportunity score
                                          │
5. STORE       Structured fields → PostgreSQL
               Text chunks + embeddings → Vector DB
                                          │
               ┌──────────────────────────┴──────────────────────────┐
               │                                                      │
6a. DASHBOARD  Aggregation queries over PostgreSQL     6b. RAG ENGINE  User query → retrieve
               render heatmaps, charts, tables                        top-K chunks → LLM generates
                                                                      cited answer
```

---

## 13. Deployment Architecture

```text
┌─────────────────────────────────────────────────────────────────┐
│                        Docker Compose / K8s                      │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │  Scraper      │  │  NLP Worker  │  │  FastAPI Backend       │ │
│  │  Containers   │  │  Containers  │  │  (API + RAG Engine)    │ │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬─────────────┘ │
│         │                 │                      │               │
│         ▼                 ▼                      ▼               │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │  Message      │  │  PostgreSQL  │  │  Vector DB             │ │
│  │  Queue        │  │              │  │  (ChromaDB / Qdrant)   │ │
│  │  (Redis/      │  │              │  │                        │ │
│  │   RabbitMQ)   │  │              │  │                        │ │
│  └──────────────┘  └──────────────┘  └────────────────────────┘ │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  React Dashboard (Nginx / CDN)                              │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 14. Future Extensibility

| Extension | Description |
| :--- | :--- |
| **Real-Time Streaming** | Replace batch ingestion with Kafka-based streaming for sub-hour data freshness. |
| **Multi-Language Support** | Extend NLP pipeline to handle Hindi, Hinglish, and regional language reviews. |
| **Alert System** | Automated alerts when a friction category spikes beyond a threshold (e.g., sudden surge in return-fee complaints after policy change). |
| **A/B Test Integration** | Correlate friction insights with Myntra's internal A/B test outcomes to measure intervention effectiveness. |
| **Competitor Benchmarking** | Extend data sources to include Ajio, Meesho, and Flipkart Fashion reviews for competitive analysis. |
| **Feedback Loop** | Allow product teams to mark insights as "actioned" and track impact on downstream KPIs. |
