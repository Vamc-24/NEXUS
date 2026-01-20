from ai_module.processor import TextProcessor
from ai_module.llm_client import get_llm_client

def run_pipeline(storage, institute_id=None):
    """
    1. Fetch unprocessed feedback
    2. Cluster it
    3. Generate Insights (Problem Statement + Solutions)
    4. Save Results
    5. Mark feedback as processed
    """
    processor = TextProcessor()
    llm = get_llm_client()

    print(f"Pipeline: Fetching feedback for institute: {institute_id}...")
    unprocessed = storage.get_unprocessed_feedback(institute_id=institute_id)
    
    # In a real scenario, we might want to maintain existing clusters and add to them,
    # or re-cluster everything to spot emerging trends.
    # For this prototype, we'll re-process specific batches or just everything available.
    if not unprocessed:
        print("Pipeline: No new feedback to process.")
        return {'status': 'no_data'}

    print(f"Pipeline: Processing {len(unprocessed)} items...")
    
    # Clustering
    clusters = processor.cluster_feedback(unprocessed, n_clusters=min(3, len(unprocessed)))
    
    processed_clusters = []
    
    for cluster in clusters:
        items = cluster['items']
        texts = [item['text'] for item in items]
        
        print(f"Pipeline: Analyzing cluster {cluster['cluster_id']} with {len(items)} items...")
        
        # LLM Generation
        problem_statement = llm.generate_problem_statement(texts)
        solutions = llm.suggest_solutions(problem_statement)
        
        processed_clusters.append({
            'theme': cluster['theme'],
            'count': len(items),
            'problem_statement': problem_statement,
            'solutions': solutions,
            'sample_texts': texts[:3] # Store a few for reference
        })

    # Sort clusters by count (frequency) descending
    processed_clusters.sort(key=lambda x: x['count'], reverse=True)

    # Save Results
    print("Pipeline: Saving results...")
    storage.save_clusters(processed_clusters, institute_id=institute_id)
    
    # Mark as processed
    feedback_ids = [item['id'] for item in unprocessed]
    storage.mark_processed(feedback_ids)
    
    print("Pipeline: Done.")
    return {'clusters': processed_clusters}
