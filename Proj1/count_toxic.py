import ast
import matplotlib.pyplot as plt

with open('non_toxic.txt', 'r') as file:
    content = file.read()

data_dict = ast.literal_eval(content)


num_non_toxic = len(data_dict)

with open('toxic.txt', 'r') as file:
    content = file.read()


data_dict = ast.literal_eval(content)
num_toxic = len(data_dict)

categories = ['Non-toxic', 'Toxic']
counts = [num_non_toxic, num_toxic]

plt.bar(categories, counts, color=['green', 'red'])
plt.ylabel('Number of Elements')
plt.title('Comparison of Toxic and Non-Toxic Elements')
plt.show()