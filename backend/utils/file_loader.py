import os, json

DATA_FILE = 'data/mock-data.json'

def read_data():
    if not os.path.exists(DATA_FILE):
        return []
    
    with open(DATA_FILE, 'r') as f:
        try:
            return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

def read_data_by_id(post_id):
    blogs = read_data()
    for blog in blogs:
        if blog['id'] == post_id:
            return blog
    return None

def save_data(data):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error occurred while saving data: {e}")
        return False
    return True