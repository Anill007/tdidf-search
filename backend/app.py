from flask import Flask, jsonify, request
from utils.file_loader import read_data, read_data_by_id, save_data
from model.vectorizer_tf_idf import tf_idf_vectorizer_service
import uuid
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:4200",
            "http://127.0.0.1:4200"
        ]
    }
})

tfidf_vectorizer = None

@app.route('/posts', methods=['GET'])
def get_posts():
    blogs = read_data()
    return jsonify(blogs), 200

@app.route('/posts/<string:post_id>', methods=['GET'])
def get_post(post_id):
    blog = read_data_by_id(post_id)

    if blog is None:
        return jsonify({'error': 'Post not found'}), 404
    
    return jsonify(blog), 200

@app.route('/posts', methods=['POST'])
def create_post():
    blog = request.get_json()
    required_fields = ['title', 'content', 'description']
    if not blog or not all(f in blog for f in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    new_blog = {
        "id": str(uuid.uuid4()),
        "title": blog['title'],
        "content": blog['content'],
        "description": blog['description']
    }
    data = read_data()
    data.append(new_blog)
    fileSaved = save_data(data)
    if not fileSaved:
        return jsonify({'error': 'Failed to save data'}), 500
    tfidf_vectorizer = tf_idf_vectorizer_service
    tfidf_vectorizer.retrain()
    return jsonify(new_blog), 201


@app.route('/posts/<string:post_id>', methods=['PUT'])
def update_post(post_id):
    data = read_data()
    updated_post = request.get_json()

    if not updated_post:
        return jsonify({"error": "Invalid JSON"}), 400

    found = False

    for post in data:
        if post.get("id") == post_id:
            post["title"] = updated_post.get("title", post["title"])
            post["description"] = updated_post.get("description", post["description"])
            post["content"] = updated_post.get("content", post["content"])
            found = True
            break

    if not found:
        return jsonify({"error": "Post not found"}), 404
    
    fileSaved = save_data(data)

    if not fileSaved:
        return jsonify({'error': 'Failed to save data'}), 500

    tfidf_vectorizer = tf_idf_vectorizer_service
    tfidf_vectorizer.retrain()

    return jsonify({"message": "Post updated successfully"}), 200

@app.route('/posts/<string:post_id>', methods=['DELETE'])
def delete_post(post_id):
    data = read_data()

    post_exists = False
    updated_data = []

    for post in data:
        if post.get("id") == post_id:
            post_exists = True
            continue
        updated_data.append(post)

    if not post_exists:
        return jsonify({"error": "Post not found"}), 404

    file_saved = save_data(updated_data)
    if not file_saved:
        return jsonify({'error': 'Failed to save data'}), 500
    
    tfidf_vectorizer = tf_idf_vectorizer_service
    tfidf_vectorizer.retrain()

    return jsonify({"message": "Post deleted successfully"}), 200

@app.route('/search', methods=['GET'])
def search_posts():
    query = request.args.get('query', '')
    similarity_threshold = float(request.args.get('similarity', 0.5))
    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400
    
    data = read_data()
    if not data:
        return jsonify({'error': 'No posts available for searching'}), 404
    
    query_similarity = tf_idf_vectorizer_service.query_similarity(query)

    filtered_results = [similar_blog for similar_blog in query_similarity if similar_blog['value'] >= similarity_threshold]
    filtered_results = [{"blog": data[item['index']], "similarity": item["value"]} for item in filtered_results]
    return jsonify(filtered_results), 200

if __name__ == '__main__':
    app.run(debug=True)