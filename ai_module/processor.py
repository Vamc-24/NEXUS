import re
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Warning: scikit-learn not found. Clustering will be mocked.")

class TextProcessor:
    def __init__(self):
        self.vectorizer = None
        if SKLEARN_AVAILABLE:
            self.vectorizer = TfidfVectorizer(
                stop_words='english',
                max_features=1000
            )

    def preprocess(self, text):
        # Basic cleaning
        text = text.lower()
        text = re.sub(r'<[^>]+>', '', text)  # remove html
        text = re.sub(r'[^a-z0-9\s]', '', text) # remove special chars
        return text

    def cluster_feedback(self, feedback_items, n_clusters=3):
        """
        Groups feedback items into clusters.
        Returns a list of dicts: {'id': cluster_id, 'items': [feedback_item, ...]}
        """
        if not feedback_items:
            return []
        
        # If we don't have enough items for clustering, just return one group
        if len(feedback_items) < n_clusters:
            return [{'cluster_id': 0, 'items': feedback_items, 'theme': 'General Feedback'}]

        if not SKLEARN_AVAILABLE:
            # Mock clustering
            return [{'cluster_id': 0, 'items': feedback_items, 'theme': 'Mock Cluster'}]

        texts = [self.preprocess(item['text']) for item in feedback_items]
        
        try:
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            kmeans.fit(tfidf_matrix)
            
            clusters = {}
            for idx, label in enumerate(kmeans.labels_):
                if label not in clusters:
                    clusters[label] = []
                clusters[label].append(feedback_items[idx])
            
            result = []
            for label, items in clusters.items():
                result.append({
                    'cluster_id': int(label),
                    'items': items,
                    'theme': f'Cluster {label + 1}' # Placeholder theme
                })
            
            return result
        except Exception as e:
            print(f"Clustering failed: {e}")
            # Fallback
            return [{'cluster_id': 0, 'items': feedback_items, 'theme': 'General'}]
