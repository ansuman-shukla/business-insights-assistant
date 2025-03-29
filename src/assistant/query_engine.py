# src/assistant/query_engine.py
from .gemini_integration import GeminiClient
from . import prompt_engineering as pe
from . import utils
import logging
import time 

try:
    from duckduckgo_search import DDGS
    SEARCH_ENABLED = True
except ImportError:
    SEARCH_ENABLED = False
    logging.warning("duckduckgo_search library not found. Real-time search functionality will be disabled. Install with: pip install -U duckduckgo-search")


logger = logging.getLogger(__name__)

class QueryEngine:
    def __init__(self):
        self.gemini_client = GeminiClient()
        self.business_profile = {
    "company_name": "Setu",
    "industry": "Financial Services",
    "size": "201-500 employees (growth from 51-200 in 2020)[3][5]",
    "primary_products": [
        "API solutions for financial onboarding (KYC, Aadhaar/PAN verification)[1][4]", 
        "Payment infrastructure (BBPS, UPI payment links)",
        "Account Aggregator services"
    ],
    "target_customer": "Fintech companies, banks, and businesses requiring financial infrastructure",
    "goals": [
        "Simplify financial integration through APIs",
        "Enable seamless bill payments and loan repayments at scale",
        "Promote financial inclusion through open-source initiatives (D91 Labs)"
    ]
}


    def _analyze_query_with_llm(self, query):
        """
        Uses the Gemini Flash model to analyze the query, determine type,
        extract entities, and suggest search queries.
        """
        logger.info(f"Analyzing query with LLM: '{query}'")
        prompt = pe.get_query_analysis_prompt(query, self.business_profile)
        analysis_result = self.gemini_client.generate_analysis(prompt)

        # Basic validation
        if isinstance(analysis_result, dict) and "error" not in analysis_result and "query_type" in analysis_result:
             logger.info(f"LLM Analysis successful: Type='{analysis_result.get('query_type')}', Entities={analysis_result.get('entities')}, Searches={analysis_result.get('required_searches')}")
             return analysis_result
        else:
             logger.error(f"LLM Analysis failed or returned invalid format: {analysis_result}")
             # Fallback or default behavior
             return {
                 "query_type": "generic",
                 "entities": {"original_query": query},
                 "required_searches": [],
                 "error": "LLM analysis failed, proceeding with generic handling."
             }

    def _fetch_realtime_data(self, search_queries, max_results_per_query=3):
        """
        Executes the suggested search queries using a search tool (DuckDuckGo example).
        """
        if not SEARCH_ENABLED or not search_queries:
            logger.info("Search disabled or no search queries provided.")
            return "" # Return empty string if search is off or no queries

        all_search_results = []
        logger.info(f"Fetching real-time data for {len(search_queries)} queries...")

        # Use the context manager for DDGS
        with DDGS() as ddgs:
            for query in search_queries:
                try:
                    logger.info(f"Searching: '{query}'")
                    # Fetch results using the text method
                    results = list(ddgs.text(query, max_results=max_results_per_query)) # Using text search

                    if results:
                        all_search_results.append(f"--- Search Results for '{query}' ---")
                        for i, result in enumerate(results):
                            # Extract title and snippet (body)
                            title = result.get('title', 'N/A')
                            snippet = result.get('body', 'N/A')
                            url = result.get('href', 'N/A')
                            all_search_results.append(f"{i+1}. Title: {title}\n   Snippet: {snippet}\n   Source: {url}")
                        all_search_results.append("--- End of Results ---")
                    else:
                         logger.info(f"No results found for query: '{query}'")
                         all_search_results.append(f"--- No significant results found online for query: '{query}' ---")

                    # Optional: Add a small delay between searches to avoid rate limiting
                    time.sleep(0.5)

                except Exception as e:
                    logger.error(f"Error during search for query '{query}': {e}", exc_info=True)
                    all_search_results.append(f"--- Error searching for query: '{query}' ---")

        logger.info(f"Finished fetching search data. Total snippets collected: approx {len(all_search_results)}")
        return "\n\n".join(all_search_results)


    def process_query(self, query):
        """
        Orchestrates the query processing: Analyze -> Search -> Generate -> Format
        """
        logger.info(f"--- Starting processing for query: '{query}' ---")

        # 1. Analyze Query using LLM (Flash model)
        analysis = self._analyze_query_with_llm(query)
        query_type = analysis.get("query_type", "generic")
        entities = analysis.get("entities", {"original_query": query})
        search_queries = analysis.get("required_searches", [])
        if "error" in analysis:
             logger.warning(f"LLM Analysis reported an error: {analysis['error']}")
             # Optionally prepend this error to the final output or handle differently

        # 2. Fetch Real-time Data based on suggested searches
        search_context = self._fetch_realtime_data(search_queries)

        # 3. Generate the Main Prompt using updated templates
        logger.info(f"Generating main prompt for type: {query_type}")
        prompt = ""
        # Ensure entities and business profile are passed correctly
        prompt_context = {
            "business_profile": self.business_profile,
            "entities": entities,
            "search_context": search_context,
            "original_query": query
        }

        # Select the appropriate detailed prompt template
        if query_type == "competitive_analysis":
            prompt = pe.get_detailed_competitive_analysis_prompt(**prompt_context)
        elif query_type == "trend_forecasting":
            prompt = pe.get_detailed_trend_forecasting_prompt(**prompt_context)
        elif query_type == "swot_analysis":
             prompt = pe.get_detailed_swot_analysis_prompt(**prompt_context)
        elif query_type == "marketing_strategy":  # <-- Add new type
            prompt = pe.get_detailed_marketing_strategy_prompt(**prompt_context)
        elif query_type == "financial_analysis": # <-- Add new type
            prompt = pe.get_detailed_financial_analysis_prompt(**prompt_context)

        else: # Generic query
            prompt = pe.get_detailed_generic_query_prompt(**prompt_context)

        # 4. Generate the Final Response using Main LLM (Pro model)
        if not prompt:
             logger.error("Failed to generate a prompt for the main LLM.")
             return "Error: Could not determine how to process the query."

        final_response = self.gemini_client.generate_response(prompt)

        # 5. Format the Response (optional refinement)
        formatted_response = self._format_response(final_response, query_type, analysis.get("error"))
        logger.info(f"--- Finished processing query: '{query}' ---")
        return formatted_response

    def _format_response(self, raw_response, query_type, analysis_error=None):
        """ Basic formatting, includes analysis errors if any. """
        if raw_response and raw_response.startswith("Error:"):
             # If the main generation failed, return that error
             return f"An error occurred during response generation:\n{raw_response}"
        elif not raw_response:
             return "Error: Received no response from the AI generation model."

        # Prepend analysis error if it occurred
        error_prefix = ""
        if analysis_error:
             error_prefix = f"**Warning:** There was an issue during the initial query analysis ({analysis_error}). The following response is based on default assumptions or potentially incomplete context.\n\n---\n\n"

        # Use Markdown for structure if not already present
        title = query_type.replace('_', ' ').title()
        formatted = f"# AI Business Insight Report: {title}\n\n"
        formatted += error_prefix # Add warning if analysis failed
        formatted += raw_response

        # Add a footer?
        formatted += "\n\n---\n*Disclaimer: This report is AI-generated based on provided context and publicly available data (as of the time of the search). Verify critical information before making decisions.*"

        return formatted