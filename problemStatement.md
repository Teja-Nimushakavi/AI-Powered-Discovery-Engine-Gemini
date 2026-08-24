# Problem Statement: AI-Powered RAG Discovery Engine for Myntra Consumer Behavior

## 1. Background & Context
As India’s leading fashion e-commerce destination, Myntra experiences millions of user interactions daily—ranging from everyday trend discovery to massive sale surges (such as the End of Reason Sale and Big Fashion Festival).

While Myntra's internal event-tracking telemetry captures funnel drops (e.g., product page views, wishlist additions, and cart abandonment), it fails to explain the psychological and cognitive friction behind these actions. To systematically improve conversion and reduce drop-offs, product and category teams need a deep, qualitative-to-quantitative intelligence layer built on authentic customer discourse.

## 2. The Core Problem
Traditional analytics treat user feedback with surface-level sentiment analysis (positive/negative/neutral) or basic text summaries. This fails to address the nuanced decision-making journey specific to Myntra shoppers.

Product managers, category heads, and UX researchers lack a unified engine to identify and quantify:
- Why users treat the Myntra Wishlist as a passive "digital closet" rather than an active buying queue.
- The exact uncertainties (fit ambiguity, fabric reality, price drops, return policies) causing purchase postponement.
- What research shoppers conduct outside Myntra before checking out.

## 3. Project Objective
Develop an end-to-end feedback intelligence system tailored to the Myntra ecosystem. The system will ingest authentic, multi-channel user conversations, structure unstructured feedback into quantifiable opportunity areas, and expose these insights through an Interactive Analytics Dashboard paired with a Retrieval-Augmented Generation (RAG) Query Engine.

## 4. Key Deliverables & System Architecture

```text
                                  [ Data Sources ]
           (Myntra Play/App Store | Reddit | YouTube Comments | X / Instagram)
                                         │
                                         ▼
                      [ Ingestion & Strict Deduplication ]
                           (Zero Synthetic Data Filter)
                                         │
                                         ▼
                  [ Vector DB + NLP Intent / Friction Extraction ]
                                         │
                   ┌─────────────────────┴─────────────────────┐
                   ▼                                           ▼
       [ Visual Analytics Dashboard ]               [ RAG Query Engine ]
  (Opportunity Heatmaps, Wishlist Friction,    (Natural Language Search grounded
    User Segment Insights, Top Drop-offs)         in authentic user citations)
```

### A. Interactive Analytics Dashboard
- **Opportunity Matrix:** Quantified friction points ranked by estimated business/conversion impact.
- **Wishlist vs. Purchase Disconnect:** Visual breakdowns of reasons for abandonment (e.g., pricing hesitation vs. sizing doubts).
- **Segment Breakdown:** Trend and behavior differences across distinct shopper profiles (e.g., Gen Z / Myntra FWD shoppers vs. Premium/Occasion buyers).

### B. RAG-Based Conversational Search Bar
- Natural language query interface for product and business teams.
- Responses must synthesize multi-channel feedback and provide direct, verbatim citations from authentic user conversations.

## 5. Core Investigative Pillars for the Discovery Engine
The discovery pipeline and RAG query bar must systematically address these core questions:

### Wishlist Dynamics:
- Why do shoppers add items to their Myntra wishlist without buying?
- What distinguishes genuine purchase intent (e.g., waiting for EORS sales, out-of-stock sizes) from casual curation/bookmarking?

### Pre-Purchase Friction & Postponement:
- What specific uncertainties emerge after a user finds a garment they like (e.g., true-to-fit sizing, color accuracy vs. studio lighting, fabric opacity, sheer/lining issues)?
- How do recent policy changes (e.g., return/convenience fees, exchange windows) affect final purchase decisions?

### External Validation Loops:
- What information do users actively seek outside Myntra prior to purchase (e.g., Instagram try-on reels, Reddit fabric reviews on r/IndianFashionAddicts, YouTube haul comparisons)?

### Comparative Evaluation:
- How do shoppers evaluate multiple shortlisted items across brands, private labels (e.g., Roadster, HRX, Anouk), and competitor pricing?

### User Segment Nuances:
- How do these friction points vary between tier-1 metro shoppers and tier-2/3 consumers, or between frequent "Myntra Insider" members and price-sensitive discount hunters?

## 6. Scope & Strict Data Constraints

| Attribute | Specification |
| :--- | :--- |
| **Platform Target** | Exclusively Myntra shopping behaviors, catalog UX, and community feedback. |
| **Data Authenticity** | Strictly real, public data. Absolutely zero synthetic, LLM-generated, or mock review data. |
| **Primary Ingestion Sources** | Google Play Store & Apple App Store reviews; Reddit communities (r/IndianFashionAddicts, r/TwoXIndia, r/myntra); YouTube try-on haul comments; public posts/replies on X (Twitter) and Instagram; verified Myntra product reviews & Q&A. |
| **Output Standard** | Must output structured insights and quantifiable opportunity areas that map directly to conversion, average order value (AOV), and return rate optimization. |
