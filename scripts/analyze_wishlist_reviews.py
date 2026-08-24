import json
import csv
import logging
from collections import Counter
from nlp.analyzer import NLPAnalyzer
from rag.generator import AnswerGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATASET_PATH = "data/raw/playstore_20260823_174830.jsonl"
CSV_OUT = "relevant_reviews.csv"
REPORT_OUT = "wishlist_analysis_report.md"

def main():
    logger.info("Initializing NLP Analyzer...")
    analyzer = NLPAnalyzer()
    
    logger.info("Loading reviews...")
    reviews = []
    with open(DATASET_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            reviews.append(json.loads(line))
            
    logger.info(f"Loaded {len(reviews)} reviews. Analyzing (this may take a while)...")
    
    relevant_reviews = []
    stats = {
        "total": len(reviews),
        "direct": 0,
        "indirect": 0,
        "not_relevant": 0,
        "barriers": Counter(),
        "behaviours": Counter()
    }
    
    for i, review in enumerate(reviews):
        if i % 100 == 0:
            logger.info(f"Processed {i}/{len(reviews)} reviews")
            
        text = review.get("content_cleaned", "")
        enriched = analyzer.enrich_record(text)
        
        relevance_top = enriched["relevance"][0]["label"] if enriched["relevance"] else "Not Relevant"
        
        if relevance_top in ["Direct", "Indirect"]:
            if relevance_top == "Direct":
                stats["direct"] += 1
            else:
                stats["indirect"] += 1
                
            barriers = [b["label"] for b in enriched["purchase_barriers"]]
            behaviours = [b["label"] for b in enriched["user_behaviours"]]
            
            for b in barriers: stats["barriers"][b] += 1
            for b in behaviours: stats["behaviours"][b] += 1
            
            relevant_reviews.append({
                "review_id": review["feedback_id"],
                "text": text,
                "relevance": relevance_top,
                "sentiment": enriched["sentiment"]["label"],
                "behaviours": ", ".join(behaviours),
                "barriers": ", ".join(barriers)
            })
        else:
            stats["not_relevant"] += 1
            
    # Save CSV
    logger.info(f"Saving {len(relevant_reviews)} relevant reviews to CSV...")
    if relevant_reviews:
        with open(CSV_OUT, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=relevant_reviews[0].keys())
            writer.writeheader()
            writer.writerows(relevant_reviews)
            
    # Generate Hypotheses with LLM
    logger.info("Generating hypotheses via LLM...")
    generator = AnswerGenerator()
    
    # Prepare context
    chunks = [{"content": r["text"], "metadata": {"source": "playstore", "sentiment": r["sentiment"]}} for r in relevant_reviews[:50]] # Limit to top 50 for context size
    
    question = "Analyze the provided reviews to identify why users abandon their wishlists. Create a PM hypotheses report following the instructions."
    
    if chunks:
        llm_response = generator.generate(question, chunks)
    else:
        llm_response = "No relevant reviews found to generate hypotheses."
        
    # Write report
    logger.info("Writing final report...")
    with open(REPORT_OUT, 'w', encoding='utf-8') as f:
        f.write("# Wishlist to Purchase Analysis Report\n\n")
        
        f.write("## 1. Dataset Overview & Relevance Analysis\n")
        f.write(f"- **Total Reviews Analysed**: {stats['total']}\n")
        f.write(f"- **Directly Relevant**: {stats['direct']}\n")
        f.write(f"- **Indirectly Relevant**: {stats['indirect']}\n")
        f.write(f"- **Not Relevant**: {stats['not_relevant']}\n")
        f.write(f"- **Relevance Percentage**: {((stats['direct'] + stats['indirect']) / stats['total']) * 100:.2f}%\n\n")
        
        f.write("## 2. Purchase-Barrier Frequency\n")
        for barrier, count in stats["barriers"].most_common():
            f.write(f"- {barrier}: {count} ({count/len(relevant_reviews)*100:.2f}%)\n")
            
        f.write("\n## 3. User Behaviour Frequency\n")
        for behaviour, count in stats["behaviours"].most_common():
            f.write(f"- {behaviour}: {count} ({count/len(relevant_reviews)*100:.2f}%)\n")
            
        f.write("\n## 4. PM Hypotheses & Product Opportunity\n")
        f.write(llm_response)
        
    logger.info("Done.")

if __name__ == "__main__":
    main()
