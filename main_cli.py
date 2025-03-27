# main_cli.py
import argparse
from src.assistant.query_engine import QueryEngine
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    parser = argparse.ArgumentParser(description="AI Business Insights Assistant (CLI)")
    parser.add_argument("query", type=str, help="Your business query")
    parser.add_argument("-o", "--output", type=str, help="Optional file path to save the report (e.g., report.md)")

    args = parser.parse_args()

    print("Initializing AI Assistant...")
    try:
        engine = QueryEngine()
        print(f"Processing your query: \"{args.query}\"")
        print("-" * 30)
        response = engine.process_query(args.query)
        print("\n--- Generated Insights ---")
        print(response)
        print("------------------------\n")

        if args.output:
            try:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(response)
                print(f"Report saved to {args.output}")
            except IOError as e:
                print(f"Error saving report to {args.output}: {e}")

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)
        print(f"An error occurred. Please check logs or try again. Details: {e}")


if __name__ == "__main__":
    main()