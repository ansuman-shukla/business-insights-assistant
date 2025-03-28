# tests/test_query_engine.py
import pytest
from unittest.mock import patch, MagicMock
from src.assistant.query_engine import QueryEngine
import datetime # Import datetime

# Mock the datetime.now() to return a fixed date for consistent testing
# Although not strictly necessary for these specific tests as we mock the header function,
# it's good practice if timestamps were used elsewhere in the tested code.
FIXED_DATE = datetime.datetime(2024, 7, 1, 10, 0, 0)

@pytest.fixture
def engine():
    """Provides a base QueryEngine instance for testing."""
    return QueryEngine()

# Test for the _analyze_query_with_llm method
@patch('src.assistant.query_engine.pe.get_query_analysis_prompt', return_value="Mock Analysis Prompt")
# Mock _fetch_realtime_data as it's part of the QueryEngine initialization/usage pattern,
# even if not directly used in this specific method test.
@patch.object(QueryEngine, '_fetch_realtime_data', return_value="Mocked search results")
def test_analyze_query_with_llm(mock_fetch, mock_get_prompt, engine):
    """
    Tests if _analyze_query_with_llm correctly processes the mocked
    LLM response for query analysis.
    """
    # Set up a mock GeminiClient for this test instance
    mock_gemini = MagicMock()
    engine.gemini_client = mock_gemini

    # Define the expected dictionary output from the mocked generate_analysis call
    mock_analysis_response = {
        "query_type": "competitive_analysis",
        "entities": {"competitors": ["Acme Corp"], "original_query": "Compare us to Acme Corp"},
        "required_searches": ["search for Acme Corp"]
    }
    # Configure the mock to return the predefined dictionary
    mock_gemini.generate_analysis.return_value = mock_analysis_response

    query = "Compare us to Acme Corp"
    # Call the method under test
    analysis_result = engine._analyze_query_with_llm(query)

    # --- Assertions ---
    # Verify that get_query_analysis_prompt was called correctly
    mock_get_prompt.assert_called_once_with(query, engine.business_profile)

    # Verify that the mocked generate_analysis was called with the expected prompt
    mock_gemini.generate_analysis.assert_called_once_with("Mock Analysis Prompt")

    # Verify that the method returned the expected dictionary
    assert analysis_result == mock_analysis_response
    assert analysis_result.get("query_type") == "competitive_analysis"


# Test for the process_query method handling a competitive analysis query
@patch('src.assistant.query_engine.pe.get_detailed_generic_query_prompt') # Mock the alternative path
@patch('src.assistant.query_engine.pe.get_detailed_competitive_analysis_prompt') # Mock the expected path
@patch('src.assistant.query_engine.pe._get_dynamic_prompt_header', return_value="[Dynamic Header]\n\n") # Mock the header for stability
@patch.object(QueryEngine, '_fetch_realtime_data', return_value="Mocked search results for Z Inc.") # Mock search
@patch.object(QueryEngine, '_analyze_query_with_llm') # Mock the analysis step
def test_process_competitive_query(mock_analyze, mock_fetch, mock_get_dynamic_header, mock_get_competitive_prompt, mock_get_generic_prompt, engine):
    """
    Tests the end-to-end process_query flow for a competitive analysis query,
    ensuring the correct prompt generation function is called.
    """
    query = "Analyse competitor Z Inc"

    # Configure the mock for _analyze_query_with_llm to return the competitive analysis type
    mock_analysis_result = {
        "query_type": "competitive_analysis",
        "entities": {"competitors": ["Z Inc"], "original_query": query},
        "required_searches": ["search for Z Inc"]
    }
    mock_analyze.return_value = mock_analysis_result

    # Configure the mock for the final response generation
    mock_gemini = MagicMock()
    engine.gemini_client = mock_gemini
    mock_gemini.generate_response.return_value = "Detailed analysis of Z Inc..."

    # Configure the mock for the specific prompt function to return a known value
    mock_get_competitive_prompt.return_value = "PROMPT_FOR_COMPETITIVE_ANALYSIS"

    # Call the method under test
    response = engine.process_query(query)

    # --- Assertions ---
    # Verify that _analyze_query_with_llm was called
    mock_analyze.assert_called_once_with(query)

    # Verify that _fetch_realtime_data was called with the correct search queries
    mock_fetch.assert_called_once_with(["search for Z Inc"])

    # Check that the specific prompt function (competitive analysis) was called
    mock_get_competitive_prompt.assert_called_once_with(
        business_profile=engine.business_profile,
        entities=mock_analysis_result['entities'],
        search_context="Mocked search results for Z Inc.",
        original_query=query
    )

    # Verify that the generic prompt function was NOT called
    mock_get_generic_prompt.assert_not_called()

    # Check that the correct prompt was passed to generate_response
    mock_gemini.generate_response.assert_called_once_with("PROMPT_FOR_COMPETITIVE_ANALYSIS")

    # Check the final formatted response structure and content
    assert "# AI Business Insight Report: Competitive Analysis" in response
    assert "Detailed analysis of Z Inc..." in response
    assert "Disclaimer: This report is AI-generated" in response


# Test for the process_query method handling a generic query
@patch('src.assistant.query_engine.pe.get_detailed_competitive_analysis_prompt') # Mock the alternative path
@patch('src.assistant.query_engine.pe.get_detailed_generic_query_prompt') # Mock the expected path
@patch('src.assistant.query_engine.pe._get_dynamic_prompt_header', return_value="[Dynamic Header]\n\n") # Mock the header for stability
@patch.object(QueryEngine, '_fetch_realtime_data', return_value="Mocked search results for generic query") # Mock search
@patch.object(QueryEngine, '_analyze_query_with_llm') # Mock the analysis step
def test_process_generic_query(mock_analyze, mock_fetch, mock_get_dynamic_header, mock_get_generic_prompt, mock_get_competitive_prompt, engine):
    """
    Tests the end-to-end process_query flow for a generic query,
    ensuring the correct prompt generation function is called.
    """
    query = "What is market share?"

    # Configure the mock for _analyze_query_with_llm to return a generic type
    mock_analysis_result = {
        "query_type": "generic_business_question", # Or "other", "generic", etc.
        "entities": {"original_query": query},
        "required_searches": ["define market share"]
    }
    mock_analyze.return_value = mock_analysis_result

    # Configure the mock for the final response generation
    mock_gemini = MagicMock()
    engine.gemini_client = mock_gemini
    mock_gemini.generate_response.return_value = "Market share explained..."

    # Configure the mock for the specific prompt function to return a known value
    mock_get_generic_prompt.return_value = "PROMPT_FOR_GENERIC_QUERY"

    # Call the method under test
    response = engine.process_query(query)

    # --- Assertions ---
    # Verify that _analyze_query_with_llm was called
    mock_analyze.assert_called_once_with(query)

    # Verify that _fetch_realtime_data was called with the correct search queries
    mock_fetch.assert_called_once_with(["define market share"])

    # Check that the generic prompt function was called
    mock_get_generic_prompt.assert_called_once_with(
        business_profile=engine.business_profile,
        entities=mock_analysis_result['entities'],
        search_context="Mocked search results for generic query",
        original_query=query
    )
    
    # Verify that the competitive analysis prompt function was NOT called
    mock_get_competitive_prompt.assert_not_called()

    # Check that the correct prompt was passed to generate_response
    mock_gemini.generate_response.assert_called_once_with("PROMPT_FOR_GENERIC_QUERY")

    # Check the final formatted response structure and content
    assert "# AI Business Insight Report: Generic Business Question" in response # Adjust title if needed
    assert "Market share explained..." in response
    assert "Disclaimer: This report is AI-generated" in response