import logging
import logging.config
logging.config.fileConfig('logging.ini')

import yaml
from model.models import SocialNetworkModel
from db.config import Session
from db.objects import Post


if __name__ == '__main__':
	settings = yaml.load(open('settings.yaml'))
	# TODO: map postgres data to nosql? local sqlite? for later inserts
	session = Session()

	# take subset of posts and authors from database (first 1000)
	logging.info('Fetching posts from database...')
	posts = session.query(Post).order_by(Post.date)[:settings['data_size']['posts']]

	logging.info('Initializing SocialNetworkModel with %d posts', len(posts))
	network_model = SocialNetworkModel(posts, settings['model']['step_duration'])

	logging.info('Executing SocialNetworkModel step')
	network_model.step()
