import csv

def create_authors_graph(filename, posts):
	with open(filename, 'w') as file:
		writer = csv.writer(file)

		for post in posts:
			for comment in post.comments:
				print (post.author_id, comment.author_id)

				writer.writerow([post.author_id, comment.author_id])

