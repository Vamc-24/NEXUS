
import os
from dotenv import load_dotenv
load_dotenv()

from ai_module.llm_client import get_llm_client

def verify_gemini():
    print(f"Checking for GEMINI_API_KEY... {'FOUND' if os.environ.get('GEMINI_API_KEY') else 'MISSING'}")
    
    client = get_llm_client()
    print(f"Client Type: {type(client).__name__}")
    
    if type(client).__name__ != 'GeminiLLMClient':
        print("FAIL: Client is not GeminiLLMClient. Check API Key and Import.")
        return

    # Test Generation
    print("\nTesting Problem Statement Generation...")
    texts = [
        "The wifi in the library is terrible, I can't study.",
        "Internet speed is too slow for video lectures.",
        "Cannot connect to eduroam in the hostel."
    ]
    
    try:
        ps = client.generate_problem_statement(texts)
        print(f"Generated Problem Statement: {ps}")
        if "Mock" in ps or ps == "Error generating problem statement.":
            print("WARNING: Output looks suspicious.")
    except Exception as e:
        print(f"FAIL: Problem Statement Generation Error: {e}")
        return

    # Test Solutions
    print("\nTesting Solution Suggestion...")
    try:
        solutions = client.suggest_solutions(ps)
        print(f"Generated {len(solutions)} Solutions.")
        print(solutions[0])
        
        if solutions[0].get('total_estimated_cost') == 'N/A':
             print("WARNING: Cost is N/A.")
    except Exception as e:
        print(f"FAIL: Solution Generation Error: {e}")

if __name__ == "__main__":
    verify_gemini()
