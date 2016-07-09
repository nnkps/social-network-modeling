import logging
import logging.config
logging.config.fileConfig('logging.ini')

import yaml

import matplotlib.pyplot as plt

from model.models import SocialNetworkModel
from db.config import ROSession, RWSession, rw_engine
from db.objects import Post, Comment, Author, Category, Base
from graph import create_authors_graph


def clone_ro_to_rw(session, rw_session, settings):
	# take subset of posts and authors from database
	logging.info('Fetching posts from database...')
	posts = session.query(Post).filter(
		Post.date.between(settings['data_options']['start_date'],
						  settings['data_options']['end_date']))
	posts_id = [post.id for post in posts]

	logging.info('Fetching comments from database...')
	comments = session.query(Comment).filter(Comment.post_id.in_(posts_id))

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

	rw_session.close()

	# real dataframe
	start_date = settings['data_options']['start_date']
	end_date = network_model.current_date

	logging.info('Start date: {} and end date: {} of real dataframe'.format(
		start_date, end_date))

	real_posts = list(session.query(Post).filter(
		Post.date.between(start_date,
						  end_date)))


	with open('statistics-end', 'w') as f:
		f.write('Number of authors: {}\n'.format(len(network_model.authors)))
		f.write('Number of comments: {}\n'.format(len(network_model.comments)))
		f.write('Number of posts: {}\n'.format(len(network_model.posts)))
		f.write('Number of categories: {}\n'.format(len(network_model.categories)))


	logging.info('Real posts number: {}'.format(len(real_posts)))
	logging.info('Creating csv for comments graph with %d', len(real_posts))
	create_authors_graph('authors-comments-real.csv', real_posts)
	session.close()
