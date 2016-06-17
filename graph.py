import csv

def create_authors_graph(filename, posts):
	with open(filename, 'w') as file:
		writer = csv.writer(file)

		for post in posts:
			for comment in post.comments:
				comment_author = comment.author_id
				post_author = post.author_id 
				print (post_author.id, comment_author.id)

				writer.writerow([post_author.id, comment_author.id])

