from mesa import Model
from mesa.time import RandomActivation
from .agents import UserAgent
from db.objects import Post, Comment, Author, Category

import logging


class SocialNetworkModel(Model):
	"""A model of social network with some user agents"""

	def __init__(self, session, step_duration):
		self.running = True
		self.schedule = RandomActivation(self)
		self.step_duration = step_duration
		self.session = session

		posts = self.session.query(Post).all()
		comments = self.session.query(Comment).all()
		authors = self.session.query(Author).all()
		categories = self.session.query(Category).all()

		logging.info('Initializing SocialNetworkModel with %d posts, %d comments, %d authors and %d categories',
			len(posts), len(comments), len(authors), len(categories))

		for author in authors:
			user_posts = list(filter(lambda post: post.author_id == author.id, posts))
			user_comments = list(filter(lambda comment: comment.author_id == author.id, comments))
			logging.info('Adding author with name %s and %d posts and %d comments',
				author.name, len(user_posts), len(user_comments))
			user = UserAgent(author.id, author.name, user_posts, user_comments)
			self.schedule.add(user)

	def step(self):
		'''Advance the model by one step'''
		self.schedule.step()
