# src/assistant/gemini_integration.py
import google.generativeai as genai
import os
from dotenv import load_dotenv
import logging
import json # For parsing structured output from routing model

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class GeminiClient:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables.")
        genai.configure(api_key=self.api_key)

        # Define models for different tasks
        # Using 1.5 Flash for routing/analysis, 1.5 Pro for generation
        # Adjust model names based on availability and your needs
        self.generative_model_name = 'gemini-2.0-flash'
        self.analysis_model_name = 'gemini-2.0-flash'

        self.generative_model = genai.GenerativeModel(self.generative_model_name)
        self.analysis_model = genai.GenerativeModel(self.analysis_model_name)
        logger.info(f"Gemini Client initialized with models: {self.generative_model_name} (gen) and {self.analysis_model_name} (analysis).")

    def _generate_with_retry(self, model, prompt, generation_config, max_retries=2):
        """Internal method to handle generation with retries for potential transient issues."""
        for attempt in range(max_retries + 1):
            try:
                response = model.generate_content(
                    prompt,
                    generation_config=generation_config
                    # Add safety_settings if needed
                )
                # Check for valid response content
                if response.candidates and response.candidates[0].content.parts:
                    if response.candidates[0].finish_reason.name == "STOP":
                        return response.text
                    else:
                        logger.warning(f"Gemini generation stopped prematurely on attempt {attempt + 1}: {response.candidates[0].finish_reason.name}")
                        # Return partial or specific message if needed based on finish_reason
                        # return f"Error: Generation stopped - {response.candidates[0].finish_reason.name}"
                elif hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
                     logger.error(f"Prompt blocked on attempt {attempt + 1}: {response.prompt_feedback.block_reason.name}")
                     return f"Error: Prompt blocked - {response.prompt_feedback.block_reason.name}"
                else:
                    logger.warning(f"Gemini response invalid or empty on attempt {attempt + 1}. Response: {response}")

            except Exception as e:
                logger.error(f"Error generating response from Gemini on attempt {attempt + 1}: {e}", exc_info=True)

            if attempt < max_retries:
                logger.info(f"Retrying Gemini call (attempt {attempt + 2}/{max_retries + 1})...")
                # Optional: Add a small delay before retrying
                # import time
                # time.sleep(1)
            else:
                logger.error(f"Gemini call failed after {max_retries + 1} attempts.")
                return f"Error: Failed to get response from Gemini after multiple attempts."
        return "Error: Max retries exceeded." # Should not be reached if loop logic is correct


    def generate_analysis(self, prompt, temperature=0.2, max_output_tokens=4096):
        """Uses the analysis model (Flash) for tasks like routing and entity extraction."""
        generation_config = genai.types.GenerationConfig(
            temperature=temperature, # Lower temp for more deterministic analysis
            max_output_tokens=max_output_tokens,
            response_mime_type="application/json" # Request JSON output
        )
        logger.info(f"Sending prompt to Analysis Model ({self.analysis_model_name})...")
        raw_response = self._generate_with_retry(self.analysis_model, prompt, generation_config)

        if raw_response and not raw_response.startswith("Error:"):
            try:
                # Gemini's JSON mode might include ```json ... ``` markers, try to strip them
                cleaned_response = raw_response.strip().removeprefix("```json").removesuffix("```").strip()
                parsed_json = json.loads(cleaned_response)
                logger.info("Successfully parsed JSON response from analysis model.")
                return parsed_json
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response from analysis model: {e}. Response was: {raw_response}")
                return {"error": "Failed to parse analysis response", "raw_response": raw_response}
        else:
            logger.error(f"Analysis model returned an error or no response: {raw_response}")
            return {"error": raw_response or "No response from analysis model"}


    def generate_response(self, prompt, temperature=0.7, max_output_tokens=4096):
        """Uses the main generative model (Pro) for detailed insights."""
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens
            # Consider response_mime_type="text/plain" if Markdown causes issues
        )
        logger.info(f"Sending prompt to Generative Model ({self.generative_model_name})...")
        response_text = self._generate_with_retry(self.generative_model, prompt, generation_config)
        logger.info(f"Received response from Generative Model (length: {len(response_text)})." if response_text and not response_text.startswith("Error:") else f"Generative model returned: {response_text}")
        return response_text