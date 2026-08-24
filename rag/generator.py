"""
Answer Generator for RAG.
Uses LangChain and Groq to synthesize an answer based on retrieved context.
"""

from __future__ import annotations

import logging
from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from config.settings import get_settings

logger = logging.getLogger(__name__)


PROMPT_TEMPLATE = """
You are an expert Product Manager for Myntra focusing on wishlist-to-purchase conversion.
Your goal is to answer the user's question about wishlist purchase barriers, utilizing both the specific retrieved feedback and the global dataset statistics.

--- GLOBAL DATASET STATISTICS ---
Total Reviews Analyzed: 1000
Primary Wishlist Purchase Barriers by frequency:
1. Size/Fit Ambiguity: 525 mentions (37% relative impact)
2. Trust Deficit (cancellations/support loops): 410 mentions (29% relative impact)
3. Quality Uncertainty: 215 mentions (15% relative impact)
4. Discount Waiting: 160 mentions (11% relative impact)
5. Choice Overload: 125 mentions (8% relative impact)
---------------------------------

Here is the retrieved context for the specific query (each chunk has a source and sentiment tag):
{context}

Question: {question}

Instructions:
1. Synthesize an answer focusing on why users add products to their wishlist but do not purchase them.
2. ALWAYS include the global percentage/frequency of the barrier mentioned in the question using the Global Dataset Statistics above.
3. NEVER start your response with phrases like "As a Product Manager at Myntra..." or any similar preambles. Just answer the question directly.
4. Do not say "I don't have enough data". If the specific context is sparse, rely on the global statistics and extrapolate reasonable insights related to the user's question.

Answer:
"""


class AnswerGenerator:
    """
    Generates answers using Google Gemini based on provided context chunks.
    """

    def __init__(self, model_name: str = "gemini-3.5-flash") -> None:
        logger.info("Initializing Answer Generator with Gemini model: %s", model_name)
        api_key = get_settings().google_api_key
        
        if not api_key:
            logger.warning("GOOGLE_API_KEY is missing. Answer generation will fail.")
            
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key or "DUMMY_KEY",
            temperature=0.0 # Keep it factual
        )
        self.prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        self.parser = StrOutputParser()
        
        self.chain = self.prompt | self.llm | self.parser

    def generate(self, question: str, retrieved_chunks: list[dict[str, Any]]) -> str:
        """
        Formats the chunks into a context string and runs the LLM generation chain.
        """
        if not retrieved_chunks:
            context_str = "No specific verbatim reviews retrieved for this exact query, but use the Global Dataset Statistics to provide a product management answer."
        else:
            context_parts = []
            for i, chunk in enumerate(retrieved_chunks):
                content = chunk["content"]
                source = chunk["metadata"].get("source", "Unknown")
                sentiment = chunk["metadata"].get("sentiment", "neutral")
                
                context_parts.append(f"--- Review {i+1} [Source: {source} | Sentiment: {sentiment}] ---\n{content}")
                
            context_str = "\n\n".join(context_parts)
        
        logger.debug("Generating answer for question: '%s'", question)
        
        try:
            # We add a dynamic instruction to the context so it always remembers not to say 'Review X' or 'Chunk X'
            context_str += "\n\nCRITICAL INSTRUCTION: Do NOT use phrases like 'Chunk 1', 'Review 2', or cite them by number in your output. Synthesize the information naturally."
            return self.chain.invoke({"context": context_str, "question": question})
        except Exception as e:
            logger.error("Failed to generate answer via Gemini: %s", e)
            return f"Error connecting to Gemini API: {str(e)}"
