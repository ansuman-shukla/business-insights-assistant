# src/backend/app.py
from flask import Flask, request, render_template, jsonify, Response
from src.assistant.query_engine import QueryEngine
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)

# Make sure the app knows where to find the src modules
# If running app.py directly, you might need path adjustments
# Or structure imports differently if using a factory pattern

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')

# In a real app, initialize engine carefully (e.g., singleton or per request context)
try:
    query_engine = QueryEngine()
    logging.info("Query Engine initialized successfully for Flask app.")
except Exception as e:
    logging.error(f"Failed to initialize Query Engine: {e}", exc_info=True)
    query_engine = None # Handle this case in routes

@app.route('/')
def index():
    return render_template('index.html') # Simple HTML form

@app.route('/ask', methods=['POST'])
def ask_assistant():
    if not query_engine:
        return jsonify({"error": "Assistant initialization failed. Please check server logs."}), 500

    query = request.form.get('query')
    if not query:
        return jsonify({"error": "Query cannot be empty."}), 400

    try:
        logging.info(f"Received query via web UI: {query}")
        response_text = query_engine.process_query(query)
        # Return as JSON, assuming the frontend will handle Markdown rendering
        return jsonify({"response": response_text})
    except Exception as e:
        logging.error(f"Error processing query via web UI: {e}", exc_info=True)
        return jsonify({"error": f"An internal error occurred: {e}"}), 500

@app.route('/download', methods=['POST'])
def download_report():
    # Assumes the frontend sends the generated report content back
    content = request.form.get('content')
    if not content:
        return jsonify({"error": "No content provided for download."}), 400

    # Basic Markdown download
    return Response(
        content,
        mimetype="text/markdown",
        headers={"Content-disposition":
                 "attachment; filename=business_insights_report.md"})



# Run the Flask app (for development)
if __name__ == '__main__':
    # Make sure .env is loaded if running directly
    from dotenv import load_dotenv
    load_dotenv()
    app.run(debug=True) # Use debug=False in production