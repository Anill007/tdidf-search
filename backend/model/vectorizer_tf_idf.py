from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from utils.file_loader import read_data

class TfidfVectorizerModel:
    def __init__(self):
        self.vectorizer = None
        self._documents = []
        self._feature_names = []
        self._matrix_array = None
        self._similarity_matrix = None
        data = read_data()
        blogs_to_docs = [f"{b['title']} {b['description']} {b['content']}" for b in data]
        self.set_documents(blogs_to_docs)

    def set_documents(self, documents=None):
        if not self.vectorizer:
            self.vectorizer = TfidfVectorizer()

        self._documents = list(documents) if documents is not None else []
        if self._documents:
            tfidf_matrix = self.vectorizer.fit_transform(self._documents)
            self._feature_names = self.vectorizer.get_feature_names_out()
            self._matrix_array = tfidf_matrix.toarray()
            self._similarity_matrix = cosine_similarity(tfidf_matrix)

    def query_similarity(self, query):
        if not self.vectorizer:
            return []
        query_vec = self.vectorizer.transform([query]).toarray()
        print(f"Query vector shape: {query_vec.shape} {query}")
        similarity_scores = cosine_similarity(query_vec, self._matrix_array).flatten()
        similarity_scores_mapped = [{"index": i, "value": v} for i, v in enumerate(similarity_scores)]
        similarity_scores_sorted = sorted(similarity_scores_mapped, key=lambda x: x["value"], reverse=True)
        return similarity_scores_sorted
    
tf_idf_vectorizer_service = TfidfVectorizerModel()