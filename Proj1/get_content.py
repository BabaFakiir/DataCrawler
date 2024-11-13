import json
import os

def read_posts_json(file_path):
    posts_data = {}

    with open(file_path, 'r') as file:
        try:
            posts = json.load(file) 

            for post in posts:
                post_id = post.get('id')       
                content = post.get('content')  
                
                if post_id and content:
                    posts_data[post_id] = content
                else:
                    print(f"Skipping post with missing id or content: {post}")
        except json.JSONDecodeError as e:
            print(f"Error reading JSON file: {e}")
    
    return posts_data

file_path = os.path.expanduser('~/Desktop/CSE472/Proj1/posts.json')

posts_dict = read_posts_json(file_path)

for post_id, content in posts_dict.items():
    print(f"Post ID: {post_id}\nContent: {content}\n")

print(len(posts_dict))
