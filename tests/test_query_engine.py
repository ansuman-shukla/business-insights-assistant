import pytest
from unittest.mock import patch, MagicMock  # Import MagicMock
from src.assistant.query_engine import QueryEngine

# --- Fixture for testing query type detection ---
@pytest.fixture
def analysis_engine():
    with patch('src.assistant.query_engine.GeminiClient') as MockGeminiClient:
        mock_instance = MockGeminiClient.return_value
        # Define different return values for each call to generate_analysis
        mock_instance.generate_analysis.side_effect = [
            # Response for "Compare us to Acme Corp"
            {"query_type": "competitive_analysis", "entities": {"competitors": ["Acme Corp"]}, "required_searches": []},
            # Response for "What are future trends in retail?"
            {"query_type": "trend_forecasting", "entities": {"industry": "retail"}, "required_searches": []},
            # Response for "Explain market segmentation"
            {"query_type": "generic", "entities": {}, "required_searches": []}
        ]
        engine = QueryEngine()
        engine.gemini_client = mock_instance
        yield engine

# --- Fixture for testing the full process flow ---
@pytest.fixture
def processing_engine():
     with patch('src.assistant.query_engine.GeminiClient') as MockGeminiClient:
        mock_instance = MockGeminiClient.return_value
        # Mock for the analysis step - simulate finding a competitor
        mock_instance.generate_analysis.return_value = {
            "query_type": "competitive_analysis",
            "entities": {"competitors": ["Z Inc"], "original_query": "Analyse competitor Z Inc"},
            "required_searches": ["search for Z Inc"]
        }
        # Mock for the response generation step
        mock_instance.generate_response.return_value = "Detailed analysis of Z Inc..."
        
        # Mock _fetch_realtime_data to return some dummy context
        with patch('src.assistant.query_engine.QueryEngine._fetch_realtime_data', return_value="Mocked search results for Z Inc."):
            engine = QueryEngine()
            engine.gemini_client = mock_instance
            yield engine


def test_analyze_query_with_llm(analysis_engine):
    """Tests if _analyze_query_with_llm correctly extracts the query type."""
    query_comp = "Compare us to Acme Corp"
    query_trend = "What are future trends in retail?"
    query_generic = "Explain market segmentation"

    # Call _analyze_query_with_llm for each query
    analysis_comp = analysis_engine._analyze_query_with_llm(query_comp)
    analysis_trend = analysis_engine._analyze_query_with_llm(query_trend)
    analysis_generic = analysis_engine._analyze_query_with_llm(query_generic)

    # Assert based on the 'query_type' key in the returned dictionaries
    assert analysis_comp.get('query_type') == "competitive_analysis"
    assert analysis_trend.get('query_type') == "trend_forecasting"
    assert analysis_generic.get('query_type') == "generic"

    # Also check that generate_analysis was called 3 times
    assert analysis_engine.gemini_client.generate_analysis.call_count == 3

def test_process_competitive_query(processing_engine):
    """Tests the end-to-end process for a competitive analysis query."""
    query = "Analyse competitor Z Inc"
    response = processing_engine.process_query(query)

    # Check that generate_analysis was called once (by _analyze_query_with_llm)
    processing_engine.gemini_client.generate_analysis.assert_called_once()

    # Check that generate_response was called once with the correct type of prompt
    processing_engine.gemini_client.generate_response.assert_called_once()
    call_args, _ = processing_engine.gemini_client.generate_response.call_args
    prompt_used = call_args[0]

    # Assert that the correct prompt components are present
    assert "Task: Conduct a detailed competitive analysis" in prompt_used
    assert "Competitors Identified: Z Inc" in prompt_used
    assert "Mocked search results for Z Inc." in prompt_used # Check context inclusion

    # Check the final formatted response
    assert "# AI Business Insight Report: Competitive Analysis" in response
    assert "Detailed analysis of Z Inc..." in response
    assert "Disclaimer: This report is AI-generated" in response