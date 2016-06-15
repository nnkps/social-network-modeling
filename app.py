import logging
import logging.config
logging.config.fileConfig('logging.ini')

import yaml
from model.models import SocialNetworkModel
from db.config import ROSession, RWSession, rw_engine
from db.objects import Post, Comment, Author, Category, Base


def clone_ro_to_rw(session, rw_session, settings):
	# take subset of posts and authors from database
	logging.info('Fetching posts from database...')
	posts = session.query(Post).order_by(Post.date)[:settings['data_size']['posts']]
	posts_id = [post.id for post in posts]

	logging.info('Fetching comments from database...')
	comments = session.query(Comment).filter(Comment.post_id.in_(posts_id))

	logging.info('Fetching authors from database...')
	authors = {post.author for post in posts} | {comment.author for comment in comments}

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


if __name__ == '__main__':
	settings = yaml.load(open('settings.yaml'))
	# TODO: map postgres data to nosql? local sqlite? for later inserts
	session = ROSession()
	Base.metadata.drop_all(rw_engine)
	Base.metadata.create_all(rw_engine)
	rw_session = RWSession()

	clone_ro_to_rw(session, rw_session, settings)
	session.close()

	network_model = SocialNetworkModel(rw_session, settings['model']['step_duration'])

	logging.info('Executing SocialNetworkModel step')
	network_model.step()

	rw_session.close()