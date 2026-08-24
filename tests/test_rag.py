"""
Tests for RAG Retriever and Generator components.
"""

from unittest.mock import patch, MagicMock

import pytest

from rag.generator import AnswerGenerator


@patch("rag.generator.ChatGoogleGenerativeAI")
def test_answer_generator(mock_llm):
    mock_llm_instance = MagicMock()
    mock_llm_instance.invoke.return_value = "This is a mock answer based on feedback."
    mock_llm.return_value = mock_llm_instance
    
    # In LCEL (LangChain Expression Language), we can mock the invoke method
    # Since self.chain = self.prompt | self.llm | self.parser
    # it's easiest to mock the final chain's invoke method directly
    
    generator = AnswerGenerator()
    generator.chain = MagicMock()
    generator.chain.invoke.return_value = "This is a synthesized answer citing [Source: PlayStore]."
    
    chunks = [
        {"content": "The fit is terrible.", "metadata": {"source": "PlayStore", "sentiment": "negative"}},
        {"content": "Sizing is ambiguous.", "metadata": {"source": "AppStore", "sentiment": "negative"}}
    ]
    
    answer = generator.generate("What is the issue with fit?", chunks)
    
    assert "synthesized answer" in answer
    generator.chain.invoke.assert_called_once()
    
    # Extract the context string passed to invoke
    invoke_args = generator.chain.invoke.call_args[0][0]
    assert "The fit is terrible." in invoke_args["context"]
    assert "Sizing is ambiguous." in invoke_args["context"]
    assert "What is the issue with fit?" == invoke_args["question"]


def test_answer_generator_empty():
    generator = AnswerGenerator()
    answer = generator.generate("Any issues?", [])
    assert "I don't have enough data" in answer
