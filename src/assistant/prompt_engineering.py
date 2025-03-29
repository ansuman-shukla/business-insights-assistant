import json
import datetime

# --- Base Prompt Elements ---


BASE_PERSONA_TEMPLATE = """You are 'Strategos', an advanced AI Business Insights Assistant specialized in providing strategic analysis and actionable recommendations for mid-size enterprises (approx. 200-1000 employees). Your analysis must be deep, context-aware, data-informed (using provided search results), and clearly structured. Assume the user is a decision-maker (CEO, Director, Head of Department) looking for practical insights, not just generic information. Use Markdown extensively for formatting (headings, lists, tables, bold text)."""

# Adjusted to be more flexible - tables are good, but allow other formats if better.
OUTPUT_FORMAT_REQUIREMENT = """Structure your response logically as a business report. Use clear headings for each section. Use Markdown for clarity (e.g., tables for direct comparisons where suitable, lists, bold text). Conclude with a dedicated 'Actionable Recommendations' section, suggesting concrete next steps, potential KPIs to track, and considerations for implementation within a mid-size company context."""

# --- NEW: Helper function to generate the dynamic header ---
def _get_dynamic_prompt_header() -> str:
    """
    Generates the initial part of the prompt including the base persona
    and the CURRENT date. Call this at the start of prompt generation functions.
    """
    current_date_str = datetime.datetime.now().strftime('%Y-%m-%d')
    # Embed the current date into the persona string dynamically
    # Adds the date information right before the final sentence for smoother flow.
    dynamic_persona = BASE_PERSONA_TEMPLATE.replace(
        "formatting (headings, lists, tables, bold text).",
        f"formatting (headings, lists, tables, bold text). CURRENT DATE IS: {current_date_str}."
    )
    return dynamic_persona + "\n\n" # Add spacing for the rest of the prompt

# --- Prompt for Query Analysis (Unaffected by Base Persona Date) ---
def get_query_analysis_prompt(query, business_profile):
    profile_str = json.dumps(business_profile, indent=2) # Format profile for clarity in prompt
    prompt = f"""Analyze the following user query submitted to an AI Business Insights Assistant.
    Your goal is to understand the user's intent, identify key entities, and determine what *current, publicly available information* needs to be searched online to provide the best possible answer.

    **Business Context:**
    The assistant serves a mid-size enterprise with the following profile:
    {profile_str}

    **DATE:** "{datetime.datetime.now().strftime('%Y-%m-%d')}"

    **User Query:**
    "{query}"

    **Your Task:**
    Respond ONLY with a JSON object containing the following keys:
    1.  `query_type`: (String) Classify the primary intent. Choose ONE from: "competitive_analysis", "trend_forecasting", "swot_analysis", "market_research", "marketing_strategy", "financial_analysis", "operational_efficiency", "generic_business_question", "other".
    2.  `entities`: (Object) Extract key entities mentioned or implied. Include keys like:
        * `competitors`: (List of strings) Specific competitor names.
        * `industry`: (String) Target industry, if specified or implied. Default to business profile if relevant.
        * `products_services`: (List of strings) Specific products/services mentioned.
        * `geography`: (String) Geographic focus, if any.
        * `time_horizon`: (String) e.g., "next quarter", "1-3 years", "long-term".
        * `focus_areas`: (List of strings) Specific aspects to analyze (e.g., "pricing", "customer reviews", "technology stack", "profitability", "marketing channels").
        * `metrics`: (List of strings) Specific KPIs or metrics mentioned (e.g., "ROI", "CAC", "EBITDA").
        * `original_query`: (String) The original user query text.
    3.  `required_searches`: (List of strings) Generate 10-15 specific, effective search engine queries (as strings) that would yield *current* information needed to thoroughly answer the user's query, considering the business context. Focus on information likely available publicly online (news, company websites, review sites, market reports summaries). Examples: "latest market share report [industry] [year]", "[Competitor Name] pricing model", "customer reviews [Competitor Name] [product]", "recent technology trends impacting [industry]", "[Industry] average financial ratios [year]", "[Competitor Name] marketing campaign analysis [year]". Avoid overly broad queries.

    **Example Output Format (Do NOT include this example in your actual response):**
    ```json
    {{
    "query_type": "competitive_analysis",
    "entities": {{
        "competitors": ["Acme Corp", "Beta Solutions"],
        "industry": "Mid-Market SaaS Solutions",
        "products_services": [],
        "geography": null,
        "time_horizon": null,
        "focus_areas": ["pricing", "customer support quality"],
        "metrics": [],
        "original_query": "How do we compare against Acme Corp and Beta Solutions on pricing and customer support?"
    }},
    "required_searches": [
        "Acme Corp SaaS pricing model 2025",
        "Beta Solutions SaaS pricing model 2025",
        "Acme Corp customer support reviews G2 Crowd",
        "Beta Solutions customer support reviews Capterra",
        "Mid-Market SaaS customer support benchmarks 2025"
    ]
    }}
    ```
    Important: Generate ONLY the JSON object as your response. Do not include explanations or introductions. Ensure the JSON is valid."""
    return prompt

# --- UPDATED: Detailed Prompt Templates (Using Dynamic Header) ---
def get_detailed_competitive_analysis_prompt(
        business_profile,
        entities,
        search_context,
        original_query):

    competitors = entities.get('competitors', [])
    focus_areas = entities.get('focus_areas', ['Overall Strategy', 'Products/Services', 'Pricing', 'Market Positioning', 'Strengths', 'Weaknesses'])
    profile_str = f"Our Company: '{business_profile['company_name']}', Industry: '{business_profile['industry']}', Size: '{business_profile['size']}', Core Products: {', '.join(business_profile['primary_products'])}"

    # --- Use the dynamic header function ---
    prompt = _get_dynamic_prompt_header()
    # --- End dynamic header usage ---

    prompt += f"**Task:** Conduct a detailed competitive analysis based on the user query and recent information.\n"
    prompt += f"**User Query:** \"{original_query}\"\n"
    prompt += f"**Our Business Profile:** {profile_str}\n"
    prompt += f"**Competitors Identified:** {', '.join(competitors) if competitors else 'General market competitors'}\n"
    prompt += f"**Specific Focus Areas:** {', '.join(focus_areas)}\n\n"

    prompt += "**Recent Information Context (from web searches):**\n"
    prompt += f"{search_context if search_context else 'No specific real-time data was fetched or available for this query.'}\n\n"

    prompt += "**Instructions for Comprehensive Analysis:**\n"
    prompt += "1.  **Executive Summary:** Start with a brief overview of the key findings and most critical strategic takeaways for OurCompany.\n"
    prompt += "2.  **Methodology:** Briefly state that the analysis is based on publicly available information, the provided search context, and general industry knowledge.\n"
    prompt += "3.  **Competitor Profiles:** For each identified competitor (and OurCompany), provide a concise profile covering:\n"
    prompt += "     * Key Offerings & Target Market\n"
    prompt += "     * Recent News/Developments (referencing search context where applicable)\n"
    prompt += "     * Perceived Strengths\n"
    prompt += "     * Perceived Weaknesses\n"
    prompt += "4.  **Comparative Analysis (Condensed Paragraph Format):** For each of the specified `focus_areas`, write a paragraph comparing OurCompany and the key competitors. Synthesize information from the search context and general knowledge. Analyze factors within these paragraphs such as:\n"
    prompt += "     * Product Features & Innovation Pace\n"
    prompt += "     * Pricing Tiers & Value Proposition\n"
    prompt += "     * Go-to-Market Strategy (Sales channels, Marketing approach)\n"
    prompt += "     * Customer Reviews & Brand Perception (cite search context if reviews were found)\n"
    prompt += "     * Estimated Market Share / Position (if discernible)\n"
    prompt += "5.  **SWOT Analysis (Derived):** Based *specifically* on the comparison above, generate a SWOT analysis (Strengths, Weaknesses, Opportunities, Threats) for OurCompany relative to these competitors.\n"
    prompt += "6.  **Strategic Differentiators & Actionable Recommendations:** This is the most critical section. Provide concrete, actionable recommendations for OurCompany. Focus on:\n"
    prompt += "     * How to leverage strengths and mitigate weaknesses.\n"
    prompt += "     * How to capitalize on opportunities and defend against threats.\n"
    prompt += "     * Suggest specific strategic differentiators (e.g., focus on a niche, enhance a specific feature, improve support, adjust pricing, form partnerships).\n"
    prompt += "     * Consider feasibility for a mid-size enterprise (resource constraints).\n"
    prompt += "     * Suggest 1-2 key metrics (KPIs) to track progress if these recommendations are implemented.\n\n"

    prompt += f"{OUTPUT_FORMAT_REQUIREMENT}\n"
    return prompt

def get_detailed_trend_forecasting_prompt(
        business_profile,
        entities,
        search_context,
        original_query):

    industry = entities.get('industry', business_profile['industry'])
    time_horizon = entities.get('time_horizon', 'next 1-3 years')
    focus_areas = entities.get('focus_areas', ['Technology', 'Market Dynamics', 'Customer Behavior', 'Regulatory Changes'])
    profile_str = f"Our Company: '{business_profile['company_name']}', Industry: '{industry}', Size: '{business_profile['size']}'"

    # --- Use the dynamic header function ---
    prompt = _get_dynamic_prompt_header()
    # --- End dynamic header usage ---

    prompt += f"**Task:** Provide a detailed trend analysis and forecast for the specified industry, focusing on implications for a mid-size enterprise.\n"
    prompt += f"**User Query:** \"{original_query}\"\n"
    prompt += f"**Our Business Profile Context:** {profile_str}\n"
    prompt += f"**Industry Focus:** {industry}\n"
    prompt += f"**Time Horizon:** {time_horizon}\n"
    prompt += f"**Specific Focus Areas:** {', '.join(focus_areas)}\n\n"

    prompt += "**Recent Information Context (from web searches):**\n"
    prompt += f"{search_context if search_context else 'No specific real-time data was fetched or available for this query.'}\n\n"

    prompt += "**Instructions for Comprehensive Analysis:**\n"
    prompt += "1.  **Executive Summary:** Briefly summarize the most impactful trends identified and the overall strategic outlook for a mid-size player in this industry over the time horizon.\n"
    prompt += "2.  **Methodology:** State that the analysis uses recent public data (including provided search context), general industry knowledge, and forecasting principles.\n"
    prompt += "3.  **Key Trend Analysis:** For each major trend identified (use the `focus_areas` and search context as guides), provide:\n"
    prompt += "     * **Trend Description:** Clearly define the trend.\n"
    prompt += "     * **Evidence/Signals:** Mention supporting data points (from search context or general knowledge).\n"
    prompt += "     * **Impact Analysis:** Analyze the potential positive and negative impacts specifically on a *mid-size enterprise* like OurCompany within this industry. Consider resource constraints and agility.\n"
    prompt += "     * **Forecast & Likelihood:** Briefly forecast the trend's likely evolution over the specified `time_horizon`. You can optionally add a qualitative likelihood (e.g., High, Medium, Low).\n"
    prompt += "     * **Categorization (Optional but helpful):** Tag the trend (e.g., Technology, Market, Social, Regulatory/Legal, Environmental).\n"
    prompt += "4.  **Cross-Trend Synergies/Conflicts:** Briefly discuss any notable interactions between the identified trends.\n"
    prompt += "5.  **Strategic Implications & Actionable Recommendations:** Provide concrete, prioritized recommendations for OurCompany:\n"
    prompt += "     * How to leverage opportunities presented by trends.\n"
    prompt += "     * How to mitigate risks posed by trends.\n"
    prompt += "     * Suggest specific initiatives (e.g., technology adoption, market repositioning, partnership strategies, talent development).\n"
    prompt += "     * Frame recommendations considering mid-size company resources (avoid suggesting massive R&D unless critical).\n"
    prompt += "     * Recommend 1-2 KPIs per major recommendation area to track adaptation and success.\n\n"

    prompt += f"{OUTPUT_FORMAT_REQUIREMENT}\n"
    return prompt

def get_detailed_swot_analysis_prompt(business_profile, entities, search_context, original_query):
    # SWOT often needs context, potentially from competitors or market position
    profile_str = f"Our Company: '{business_profile['company_name']}', Industry: '{business_profile['industry']}', Size: '{business_profile['size']}', Core Products: {', '.join(business_profile['primary_products'])}"
    focus = entities.get('focus_areas', ["overall business"]) # What aspect to SWOT?

    # --- Use the dynamic header function ---
    prompt = _get_dynamic_prompt_header()
    # --- End dynamic header usage ---

    prompt += f"**Task:** Conduct a detailed SWOT analysis (Strengths, Weaknesses, Opportunities, Threats) for OurCompany.\n"
    prompt += f"**User Query:** \"{original_query}\"\n"
    prompt += f"**Our Business Profile:** {profile_str}\n"
    prompt += f"**Focus of SWOT:** {' '.join(focus)}\n\n"

    prompt += "**Recent Information Context (from web searches relevant to market/competitors):**\n"
    prompt += f"{search_context if search_context else 'No specific real-time data was fetched. Analysis based on general knowledge and business profile.'}\n\n"

    prompt += "**Instructions for Comprehensive SWOT Analysis:**\n"
    prompt += "1.  **Introduction:** Briefly state the purpose of the SWOT analysis for OurCompany focusing on the specified area.\n"
    prompt += "2.  **Methodology:** Mention reliance on the business profile, provided search context (if any), and general industry understanding.\n"
    prompt += "3.  **Internal Analysis:**\n"
    prompt += "     * **Strengths:** Identify internal capabilities, resources, and advantages relative to the market/competitors. Be specific (e.g., 'Proprietary algorithm', 'Strong regional presence', 'Experienced engineering team'). List at least 3-5 key strengths.\n"
    prompt += "     * **Weaknesses:** Identify internal limitations, resource gaps, or disadvantages. Be honest and specific (e.g., 'Limited marketing budget', 'Dependency on single supplier', 'Aging technology stack'). List at least 3-5 key weaknesses.\n"
    prompt += "4.  **External Analysis:**\n"
    prompt += "     * **Opportunities:** Identify external factors or trends (use search context) that OurCompany could potentially leverage for growth or advantage (e.g., 'Growing demand in adjacent market', 'Competitor product recall', 'New favorable regulation', 'Emerging technology partnership'). List at least 3-5 key opportunities.\n"
    prompt += "     * **Threats:** Identify external factors or trends that could negatively impact OurCompany (e.g., 'New entrant with lower pricing', 'Changing customer preferences', 'Economic downturn impacting client budgets', 'Potential cybersecurity risks'). List at least 3-5 key threats.\n"
    prompt += "5.  **SWOT Matrix Summary:** Present the findings clearly, perhaps using Markdown lists under each heading (S, W, O, T).\n"
    prompt += "6.  **Strategic Implications & Actionable Recommendations:** This is crucial. Analyze the interactions within the SWOT matrix (TOWS analysis approach can be useful mentally):\n"
    prompt += "     * **SO Strategies (Strength-Opportunity):** How to use strengths to exploit opportunities?\n"
    prompt += "     * **WO Strategies (Weakness-Opportunity):** How to overcome weaknesses by taking advantage of opportunities?\n"
    prompt += "     * **ST Strategies (Strength-Threat):** How to use strengths to avoid or mitigate threats?\n"
    prompt += "     * **WT Strategies (Weakness-Threat):** What defensive actions are needed to prevent weaknesses from making the company vulnerable to threats?\n"
    prompt += "     * Provide 3-5 prioritized, actionable recommendations based on these strategic implications, suitable for a mid-size enterprise.\n\n"

    prompt += f"{OUTPUT_FORMAT_REQUIREMENT}\n"
    return prompt

# --- NEWLY ADDED FUNCTION ---
def get_detailed_generic_query_prompt(
        business_profile,
        entities,
        search_context,
        original_query):

    profile_str = f"Our Company: '{business_profile['company_name']}', Industry: '{business_profile['industry']}', Size: '{business_profile['size']}'"

    # --- Use the dynamic header function ---
    prompt = _get_dynamic_prompt_header()
    # --- End dynamic header usage ---

    prompt += f"**Task:** Address the following business query comprehensively, providing insights relevant to a mid-size enterprise.\n"
    prompt += f"**User Query:** \"{original_query}\"\n"
    prompt += f"**Our Business Profile Context:** {profile_str}\n\n"

    prompt += "**Potentially Relevant Context (from web searches):**\n"
    prompt += f"{search_context if search_context else 'No specific real-time data was fetched for this query.'}\n\n"

    prompt += "**Instructions for Comprehensive Response:**\n"
    prompt += "1.  **Deconstruct the Query:** Clearly state your understanding of the user's core question and objective(s).\n"
    prompt += "2.  **Identify Key Concepts:** Define or explain any central business terms or concepts relevant to the query.\n"
    prompt += "3.  **Structured Analysis:** Break down the answer into logical sections. Consider multiple perspectives (e.g., financial, operational, marketing, strategic) if applicable.\n"
    prompt += "4.  **Incorporate Context:** Relate the analysis specifically to a *mid-size enterprise* context. How might the answer differ for a large corporation or a small startup? Use the business profile and search context where relevant.\n"
    prompt += "5.  **Provide Nuance:** Discuss pros and cons, potential challenges, assumptions, and trade-offs related to the query or potential solutions.\n"
    prompt += "6.  **Use Examples (if applicable):** Illustrate points with brief, relevant examples (hypothetical or based on general knowledge).\n"
    prompt += "7.  **Actionable Insights/Recommendations (if appropriate):** If the query implies seeking advice or solutions, conclude with clear, actionable steps or strategic considerations suitable for the target company profile. If the query is purely informational, summarize the key takeaways.\n\n"

    prompt += f"{OUTPUT_FORMAT_REQUIREMENT}\n"
    return prompt
# --- END NEWLY ADDED FUNCTION ---


# --- START NEW FUNCTION: get_detailed_financial_analysis_prompt ---
def get_detailed_financial_analysis_prompt(
        business_profile,
        entities,
        search_context,
        original_query):

    industry = entities.get('industry', business_profile['industry'])
    time_horizon = entities.get('time_horizon', 'latest reported period / next 12 months')
    focus_areas = entities.get('focus_areas', ['Profitability', 'Liquidity', 'Solvency', 'Efficiency Ratios', 'Cash Flow Analysis'])
    metrics = entities.get('metrics', []) # Specific KPIs requested by user
    competitors = entities.get('competitors', []) # For benchmarking if requested/relevant
    profile_str = f"Our Company: '{business_profile['company_name']}', Industry: '{industry}', Size: '{business_profile['size']}'"

    # --- Use the dynamic header function ---
    prompt = _get_dynamic_prompt_header()
    # --- End dynamic header usage ---

    prompt += f"**Task:** Conduct a detailed financial analysis based on the user query, focusing on the specified areas and their implications for a mid-size enterprise.\n"
    prompt += f"**User Query:** \"{original_query}\"\n"
    prompt += f"**Our Business Profile Context:** {profile_str}\n"
    prompt += f"**Industry Focus:** {industry}\n"
    prompt += f"**Time Horizon:** {time_horizon}\n"
    prompt += f"**Specific Focus Areas:** {', '.join(focus_areas)}\n"
    if metrics:
        prompt += f"**Specific Metrics Requested:** {', '.join(metrics)}\n"
    if competitors:
        prompt += f"**Competitors for Benchmarking:** {', '.join(competitors)}\n"
    prompt += "\n"

    prompt += "**Recent Information Context (from web searches - e.g., industry benchmarks, competitor financial summaries):**\n"
    prompt += f"{search_context if search_context else 'No specific real-time financial data or benchmarks were fetched. Analysis based on general principles and business profile.'}\n\n"

    prompt += "**Instructions for Comprehensive Financial Analysis:**\n"
    prompt += "1.  **Executive Summary:** Provide a high-level overview of the company's perceived financial health based on the analysis, highlighting key strengths, weaknesses, and critical recommendations.\n"
    prompt += "2.  **Methodology:** Briefly state that the analysis relies on general financial principles, the business profile, potentially provided search context (industry averages, competitor data snippets), and the specific user query focus.\n"
    prompt += "3.  **Analysis by Key Financial Area:** For each specified `focus_area` (or standard areas if none specified):\n"
    prompt += "     * **Define Key Metrics:** Explain the relevant financial ratios or metrics within this area (e.g., Gross Profit Margin for Profitability, Current Ratio for Liquidity, Debt-to-Equity for Solvency, Asset Turnover for Efficiency).\n"
    prompt += "     * **Assess Performance:** Analyze the likely performance in this area based on general knowledge of mid-size businesses in this industry and any data points from the search context. Discuss trends if applicable (e.g., improving/declining margins).\n"
    prompt += "     * **Industry Context/Benchmarking:** Compare performance against typical benchmarks for mid-size companies in this industry, or against specific competitors if data is available/requested. Use search context here if applicable.\n"
    prompt += "     * **Implications for Mid-Size Enterprise:** Discuss what these findings mean specifically for a company of this size (e.g., impact of tight cash flow on growth, ability to secure loans).\n"
    prompt += "4.  **Cash Flow Analysis (if applicable):** Detail the importance of cash flow (Operating, Investing, Financing) for sustainability and growth in a mid-size context.\n"
    prompt += "5.  **Overall Financial Health Assessment:** Synthesize the findings into a concluding assessment of the company's financial strengths and weaknesses.\n"
    prompt += "6.  **Strategic Financial Recommendations:** Provide actionable financial strategies tailored for a mid-size enterprise:\n"
    prompt += "     * Suggestions for improving profitability, managing cash flow, optimizing capital structure, controlling costs, or making investment decisions.\n"
    prompt += "     * Consider resource limitations and access to capital typical for mid-size firms.\n"
    prompt += "     * Recommend 2-3 key financial KPIs (beyond those perhaps already requested) to monitor financial health and track the impact of recommendations (e.g., 'Days Sales Outstanding', 'Operating Cash Flow Margin', 'Interest Coverage Ratio').\n\n"

    prompt += f"{OUTPUT_FORMAT_REQUIREMENT}\n"
    return prompt
# --- END NEW FUNCTION: get_detailed_financial_analysis_prompt ---


# --- START NEW FUNCTION: get_detailed_marketing_strategy_prompt ---
def get_detailed_marketing_strategy_prompt(
        business_profile,
        entities,
        search_context,
        original_query):

    industry = entities.get('industry', business_profile['industry'])
    products_services = entities.get('products_services', business_profile['primary_products'])
    geography = entities.get('geography', 'Not specified')
    focus_areas = entities.get('focus_areas', ['Target Audience Analysis', 'Value Proposition', 'Channel Strategy (Digital & Offline)', 'Content Marketing', 'Brand Positioning'])
    competitors = entities.get('competitors', []) # For competitive marketing analysis
    metrics = entities.get('metrics', []) # Specific marketing KPIs requested
    profile_str = f"Our Company: '{business_profile['company_name']}', Industry: '{industry}', Size: '{business_profile['size']}'"

    # --- Use the dynamic header function ---
    prompt = _get_dynamic_prompt_header()
    # --- End dynamic header usage ---

    prompt += f"**Task:** Develop or analyze a marketing strategy based on the user query, tailored for a mid-size enterprise in the specified industry.\n"
    prompt += f"**User Query:** \"{original_query}\"\n"
    prompt += f"**Our Business Profile Context:** {profile_str}\n"
    prompt += f"**Industry Focus:** {industry}\n"
    prompt += f"**Product/Service Focus:** {', '.join(products_services)}\n"
    prompt += f"**Geographic Scope:** {geography}\n"
    prompt += f"**Specific Focus Areas:** {', '.join(focus_areas)}\n"
    if competitors:
        prompt += f"**Competitors for Marketing Comparison:** {', '.join(competitors)}\n"
    if metrics:
        prompt += f"**Specific Metrics Requested:** {', '.join(metrics)}\n"
    prompt += "\n"

    prompt += "**Recent Information Context (from web searches - e.g., competitor campaigns, industry marketing trends, customer reviews):**\n"
    prompt += f"{search_context if search_context else 'No specific real-time marketing data was fetched. Analysis based on general principles, business profile, and user query.'}\n\n"

    prompt += "**Instructions for Comprehensive Marketing Strategy Analysis:**\n"
    prompt += "1.  **Executive Summary:** Briefly summarize the core marketing challenge or opportunity, key findings, and the most critical strategic marketing recommendations.\n"
    prompt += "2.  **Methodology:** State reliance on the business profile, user query, general marketing principles, and any provided search context (competitor activities, trends).\n"
    prompt += "3.  **Market & Customer Understanding:**\n"
    prompt += "     * **Target Audience:** Define or refine the likely primary and secondary target customer segments for the specified products/services in this industry. Consider demographics, psychographics, pain points, and buying behavior.\n"
    prompt += "     * **Market Landscape:** Briefly describe the competitive environment and any relevant market trends impacting marketing (use search context).\n"
    prompt += "4.  **Analysis of Marketing Strategy Components (based on `focus_areas`):**\n"
    prompt += "     * **Value Proposition & Positioning:** Articulate a compelling value proposition. How should the company position itself against competitors (use search context for competitor positioning if available)?\n"
    prompt += "     * **Channel Mix:** Evaluate potential marketing channels (e.g., SEO, SEM, Content, Social Media, Email, Partnerships, Events, Sales Team Support). Recommend a cost-effective mix suitable for a mid-size budget. Analyze competitor channels if data exists.\n"
    prompt += "     * **Messaging & Content:** Outline key marketing messages. Suggest types of content (blog posts, case studies, webinars, videos) that would resonate with the target audience and support the channel strategy.\n"
    prompt += "     * **Digital Presence:** Assess the importance and potential optimization areas for website, SEO, and social media.\n"
    prompt += "     * **Budget Considerations:** Discuss typical marketing budget allocation approaches for mid-size companies in this sector (even if specific numbers aren't available).\n"
    prompt += "5.  **Competitor Marketing Snapshot (if applicable):** Briefly analyze the apparent marketing strategies of key competitors identified (channels used, messaging, estimated strengths/weaknesses) based on search context.\n"
    prompt += "6.  **Actionable Marketing Recommendations:** Provide specific, prioritized marketing initiatives:\n"
    prompt += "     * Suggest concrete campaigns, channel optimizations, content ideas, or strategic shifts.\n"
    prompt += "     * Emphasize tactics with measurable ROI and feasibility for a mid-size enterprise (e.g., focus on niche marketing, leverage digital tools effectively, build community).\n"
    prompt += "     * Recommend 2-3 key marketing KPIs (e.g., 'Customer Acquisition Cost (CAC)', 'Lead Conversion Rate', 'Website Traffic Growth', 'Social Media Engagement Rate') to measure success.\n\n"

    prompt += f"{OUTPUT_FORMAT_REQUIREMENT}\n"
    return prompt