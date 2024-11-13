from mastodon import Mastodon
import json
import os
from datetime import datetime
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from bs4 import BeautifulSoup


# Create an instance of the Mastodon class
mastodon = Mastodon(
    access_token='QKc_CzdDTNxF-eAkFCx6-SsUvtURQ4BhU3OuXJxdPB4',
    api_base_url='https://mastodon.social'
)

#-------------------------------------------Step 2-------------------------------------------------------

#-------------------Find posts json------------------------

# Hashtags to search
hashtags_red = ['#trump', '#trumplies', '#trump2024', '#TrumpIsUnfitForOffice', '#trumpforprison',
                '#trumpisafelon', '#TrumpIsALiar', '#TrumpCrimes', '#TrumpMedia', '#donaldtrump',
                '#republican', '#trump2024', '#conservative', '#trumpet', '#trumptrain', '#strumpfhose',
                '#presidenttrump', '#conservatives', '#womenfortrump', '#fucktrump', '#buildthewall',
                '#makeamericagreatagain', '#keepamericagreat', '#election', '#vote', '#politics', '#usa', '#news']

hashtags_blue = ['#biden', '#elections', '#democrat', '#joebiden', '#congress', '#electionday', '#democracy',
                '#president', '#voting', '#voteblue', '#votered', '#liberal', '#KamalaHarris', '#DemocratsDelivery',
                '#democratsdidthat', '#DemocratsGetTheJobDone', '#democratswantdemocracy', '#democrats2024',
                '#democratsforthepeople', '#democratsrock', '#democratsrule', '#DemocratsUnited',
                '#BidenHarris', '#BidenAdministration', '#BidenRocks']

results = []

for hashtag in hashtags_red + hashtags_blue:
    search_results = mastodon.search_v2(q=hashtag, result_type='statuses', resolve=True)
    results.append(search_results)

json_file_path_posts = os.path.expanduser('~/Desktop/CSE472/Proj1/posts.json')

# Custom function to handle datetime serialization
def convert_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError("Type not serializable")

# Function to clean the content and extract readable text
def clean_html_content(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text(separator=" ").strip()  

# Function to fetch comments and boosts for each post
def fetch_post_details(post_id):
    comments = []
    boosts = []

    try:
        context = mastodon.status_context(post_id)
        comments = context['descendants']  # This will give the replies
    except Exception as e:
        print(f"Error fetching comments for post {post_id}: {e}")

    try:
        boosts = mastodon.status_reblogged_by(post_id)
    except Exception as e:
        print(f"Error fetching boosts for post {post_id}: {e}")

    return comments, boosts

# Write search results to a JSON file
with open(json_file_path_posts, 'w') as json_file:
    all_statuses = []
    for result in results:
        for post in result['statuses']:
            post_id = post['id']
            comments, boosts = fetch_post_details(post_id)

            if 'content' in post:
                post['content'] = clean_html_content(post['content'])

            post['comments'] = comments
            post['boosts'] = boosts
            all_statuses.append(post)
    
    json.dump(all_statuses, json_file, indent=4, default=convert_datetime)

#-------------------Find user json------------------------
username = ['Trump@mastodon.xyz', 'VP46@c.im', 'VP@femboys.love']
user_ids = []
for i in username:
    account_info = mastodon.account_search(i)
    user_ids.append(account_info[0]['id'])

map_users = {}
followers_list = []
queue = user_ids[:]  
total_followers = 0  

while queue and total_followers < 350:
    current_user_id = queue.pop(0)  
    try:
        followers_one_user = mastodon.account_followers(current_user_id, limit=100)
        followers_list.extend(followers_one_user)
        map_users[current_user_id] = followers_one_user

        # Add followers' ids to the queue if we haven't reached 350 followers
        if total_followers + len(followers_one_user) <= 350:
            for follower in followers_one_user:
                queue.append(follower['id'])

        total_followers += len(followers_one_user)
    except Exception as e:
        print(f"Error fetching followers for user {current_user_id}: {e}")
        continue  

# Write the followers_list to a JSON file
json_file_path_users = os.path.expanduser('~/Desktop/CSE472/Proj1/users.json')
with open(json_file_path_users, 'w') as json_file:
    json.dump(followers_list, json_file, indent=4, default=convert_datetime)

#-------------------------------------------/Step 2 end-------------------------------------------------------

#---------------------------------------------Step 3---------------------------------------------------------

#--------------post-repost-reply graph-----------------
G_post = nx.DiGraph()

# Adding posts to the graph with post id as the node identifier
for post in all_statuses:
    post_id = post['id']
    G_post.add_node(post_id, type='post')

    for comment in post['comments']:
        comment_id = comment['id']
        G_post.add_node(comment_id, type='comment')
        G_post.add_edge(post_id, comment_id, relation='reply')

    for boost in post['boosts']:
        boost_id = boost['id']
        G_post.add_node(boost_id, type='boost')
        G_post.add_edge(post_id, boost_id, relation='boost')

nx.write_gml(G_post, os.path.expanduser('~/Desktop/CSE472/Proj1/post_graph.gml'))

#--------------user graph undirected----------------
G_user = nx.Graph()

#Adding seed users (keys of map_users dict) as root nodes
for user_id, followers in map_users.items():
    G_user.add_node(user_id, type='user')  

    for follower in followers:
        follower_id = follower['id']  
        G_user.add_node(follower_id, type='follower')  
        G_user.add_edge(user_id, follower_id)  

#Save the graph to a .gml file
nx.write_gml(G_user, os.path.expanduser('~/Desktop/CSE472/Proj1/user_graph.gml'))

#----------------Step 4.1---------------------
# done in ipynb Link: https://colab.research.google.com/drive/1v9h-WH94hyO2a6ul3kTVI5SQzdKyXQiU?usp=sharing

#----------------Step 4.2---------------------
#Degree distribution and histogram

degree_sequence = [d for n, d in G_user.degree()]

plt.figure(figsize=(10, 6))

plt.hist(degree_sequence, bins=range(min(degree_sequence), max(degree_sequence) + 1), edgecolor='black', alpha=0.7)

plt.title("Degree Distribution of User Graph", fontsize=16)
plt.xlabel("Degree", fontsize=14)
plt.ylabel("Frequency", fontsize=14)

plt.show()

#Calculate Closeness Centrality
closeness_centrality = nx.closeness_centrality(G_user)
# Plotting the Closeness Centrality histogram
plt.figure(figsize=(10, 6))
plt.hist(closeness_centrality.values(), bins=20, color='blue', edgecolor='black')
plt.title('Closeness Centrality Distribution')
plt.xlabel('Closeness Centrality')
plt.ylabel('Frequency')
plt.grid(True)
plt.show()

#Calculate Betweenness Centrality
betweenness_centrality = nx.betweenness_centrality(G_user)
plt.figure(figsize=(10, 6))
plt.hist(betweenness_centrality.values(), bins=20, color='green', edgecolor='black')
plt.title('Betweenness Centrality Distribution')
plt.xlabel('Betweenness Centrality')
plt.ylabel('Frequency')
plt.grid(True)
plt.show()

#1 hop friends average
# Ensure the graph is connected; otherwise, calculate for the largest connected component
if not nx.is_connected(G_user):
    largest_cc = max(nx.connected_components(G_user), key=len)
    G_largest_cc = G_user.subgraph(largest_cc).copy()
else:
    G_largest_cc = G_user

local_averages = {}

for node in G_largest_cc.nodes:
    degree = G_largest_cc.degree(node)  
    local_averages[node] = degree  

print("Local (1-hop) Average Friends for Each Node:")
for node, avg in local_averages.items():
    print(f"Node {node}: {avg} friends")


# 2. Global Level: Overall Average Number of Friends

degrees = [degree for node, degree in G_largest_cc.degree()]
global_average = np.mean(degrees)
print(f"\nGlobal Average Number of Friends (Across Entire Network): {global_average:.2f}")

