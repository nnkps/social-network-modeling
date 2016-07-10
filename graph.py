import csv

def create_authors_graph(filename, comments):
	with open(filename, 'w') as file:
		writer = csv.writer(file)

		for comment in comments:
			writer.writerow([comment.post.author_id, comment.author_id])

