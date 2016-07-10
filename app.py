import logging
import logging.config
logging.config.fileConfig('logging.ini')
import os
from functools import reduce
from datetime import datetime, timedelta

import yaml
from sqlalchemy import and_, func
import matplotlib.pyplot as plt

from model.models import SocialNetworkModel
from db.config import ROSession, RWSession, rw_engine
from db.objects import Post, Comment, Author, Category, Base
from graph import create_authors_graph


def get_statistics(session, directory, start_date, end_date, authors_id):
	if not os.path.exists(directory):
		os.makedirs(directory)

	posts = list(session.query(Post).filter(
		and_(
			Post.date.between(start_date, end_date),
			Post.author_id.in_(authors_id)
		)
	))
	posts_id = [post.id for post in posts]
	comments = list(session.query(Comment).filter(
		and_(
			Comment.date.between(start_date, end_date),
			Comment.post_id.in_(posts_id)
		)
	))
	if directory == 'simulated':
		comments = list(session.query(Comment).filter(
			Comment.date.between(start_date, end_date)
		))

	comments_id = [comment.id for comment in comments]
	categories = list(session.query(Category).all())

	def get_min_max_avg(table, table_column, filter_range):
		counts = list(session.query(table_column, func.count(table_column)).\
			group_by(table_column).\
			filter(table.id.in_(filter_range)))

		minimum = 0
		maximum = 0
		average = 0
		if counts:
			count_values = [item[1] for item in counts]

			if counts == len(authors_id):
				minimum = min(count_values)
			maximum = max(count_values)

			average = sum(count_values) / len(authors_id)

		return minimum, maximum, average
	print(directory)
	# print(comments)
	comments_per_author = get_min_max_avg(Comment, Comment.author_id, comments_id)
	posts_per_author = get_min_max_avg(Post, Post.author_id, posts_id)
	comments_per_post = get_min_max_avg(Comment, Comment.post_id, comments_id)

	with open(directory + '/statistics.yaml', 'w') as f:
		print_to_file = lambda text: print(text, file=f)
		get_only_date = lambda date: date.strftime('%Y-%m-%d') if isinstance(date, datetime) else date
		print_to_file('Start date: {}'.format(get_only_date(start_date)))
		print_to_file('End date: {}'.format(get_only_date(end_date)))
		print_to_file('Number of authors: {}'.format(len(authors_id)))
		print_to_file('Number of comments: {}'.format(len(comments)))
		print_to_file('Number of posts: {}'.format(len(posts)))
		print_to_file('Number of categories: {}'.format(len(categories)))
		print_to_file('Number of comments per author:')
		print_to_file('\tmin: {}'.format(comments_per_author[0]))
		print_to_file('\tmax: {}'.format(comments_per_author[1]))
		print_to_file('\tavg: {}'.format(comments_per_author[2]))
		print_to_file('Number of posts per user:')
		print_to_file('\tmin: {}'.format(posts_per_author[0]))
		print_to_file('\tmax: {}'.format(posts_per_author[1]))
		print_to_file('\tavg: {}'.format(posts_per_author[2]))
		print_to_file('Number of comments per post:')
		print_to_file('\tmin: {}'.format(comments_per_post[0]))
		print_to_file('\tmax: {}'.format(comments_per_post[1]))
		print_to_file('\tavg: {}'.format(comments_per_post[2]))
	logging.info('Creating csv for comments graph with %d', len(posts))
	create_authors_graph(directory + '/authors-comments.csv', posts)

def clone_ro_to_rw(session, rw_session, settings):
	# take subset of posts and authors from database
	logging.info('Fetching posts from database...')
	posts = session.query(Post).filter(
		Post.date.between(settings['data_options']['start_date'],
						  settings['data_options']['end_date']))
	posts_id = [post.id for post in posts]

	logging.info('Fetching comments from database...')
	comments = session.query(Comment).filter(
		and_(
			Comment.post_id.in_(posts_id),
			Comment.date.between(settings['data_options']['start_date'],
						  	     settings['data_options']['end_date'])
		)
	)

	logging.info('Fetching authors from database...')
	authors_id = {post.author_id for post in posts} | {comment.author_id for comment in comments}
	authors = session.query(Author).filter(Author.id.in_(authors_id))

	logging.info('Fetching categories from database...')
	categories = session.query(Category).all()

	for post in posts:
		rw_session.add(Post(id=post.id, date=post.date, category_id=post.category_id, author_id=post.author_id))

	for comment in comments:
		rw_session.add(Comment(id=comment.id, date=comment.date, author_id=comment.author_id, post_id=comment.post_id))

	for author in authors:
		rw_session.add(Author(id=author.id, name=author.name))

	for category in categories:
		rw_session.add(Category(id=category.id, category_name=category.category_name))

	rw_session.commit()

def show_comments_histogram(network_model, filename):
	plt.clf()
	plt.hist([len(agent.comments) for agent in network_model.schedule.agents])
	plt.savefig(filename)

def show_posts_histogram(network_model, filename):
	plt.clf()
	plt.hist([len(agent.posts) for agent in network_model.schedule.agents])
	plt.savefig(filename)

if __name__ == '__main__':
	settings = yaml.load(open('settings.yaml'))

	session = ROSession()

	Base.metadata.drop_all(rw_engine)
	Base.metadata.create_all(rw_engine)
	rw_session = RWSession()

	clone_ro_to_rw(session, rw_session, settings)

	network_model = SocialNetworkModel(rw_session,
									   **settings['model'])
	with open('statistics', 'w') as f:
		f.write('Number of authors: {}\n'.format(len(network_model.authors)))
		f.write('Number of comments: {}\n'.format(len(network_model.comments)))
		f.write('Number of posts: {}\n'.format(len(network_model.posts)))
		f.write('Number of categories: {}\n'.format(len(network_model.categories)))

	# Comments histogram for users
	logging.info('Showing histogram for posting before simulation')
	show_posts_histogram(network_model, 'posts_histogram_start.png')

	logging.info('Showing histogram for commenting before simulation')
	show_comments_histogram(network_model, 'comments_histogram_start.png')
	
	logging.info('Executing SocialNetworkModel steps')
	network_model.run_model()

	logging.info('Showing histogram for posting after simulation')
	show_posts_histogram(network_model, 'posts_histogram_end.png')

	logging.info('Showing histogram for commenting after simulation')
	show_comments_histogram(network_model, 'comments_histogram_end.png')

	avg_commenting = network_model.datacollector.get_model_vars_dataframe()
	avg_commenting.plot()
	plt.savefig('avg_commenting.png')

	logging.info('Creating csv for comments graph')
	create_authors_graph('authors-comments.csv', network_model.posts)

	# get statistics
	start_date = network_model.start_date
	end_date = network_model.current_date
	authors_id = list(map(lambda author: author.id, network_model.authors))

	# simulated dataframe
	get_statistics(rw_session, 'simulated', start_date, end_date, authors_id)
	rw_session.close()

	# training dataframe
	get_statistics(session, 'training', settings['data_options']['start_date'], settings['data_options']['end_date'], authors_id)

	# real dataframe
	get_statistics(session, 'real', start_date, end_date, authors_id)
	session.close()
