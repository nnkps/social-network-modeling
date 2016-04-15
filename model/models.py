from mesa import Model
from mesa.time import RandomActivation
from .agents import UserAgent

import logging


class SocialNetworkModel(Model):
	"""A model of social network with some user agents"""
	# TODO: pass more users' data from database to model
	def __init__(self, posts, step_duration):
		self.running = True
		self.schedule = RandomActivation(self)
		self.step_duration = step_duration

		authors = {post.author for post in posts}

		for author in authors:
			user_posts = list(filter(lambda post: post.author_id == author.id, posts))
			logging.info('Adding author with name %s and %d posts',
				author.name, len(user_posts))
			user = UserAgent(author.id, author.name, user_posts)
			self.schedule.add(user)

	def step(self):
		'''Advance the model by one step'''
		self.schedule.step()
