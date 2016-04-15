from mesa import Agent
from math import ceil

import logging


class UserAgent(Agent):
	"""An agent with user behavior"""
	def __init__(self, unique_id, name, posts):
		self.unique_id = unique_id
		self.name = name
		self.posts = posts

	def frequency_of_posting(self):
		self.posts.sort(key=lambda post: post.date)
		first, last = self.posts[0], self.posts[-1]
		return len(self.posts) / (last.date - first.date).days

	def how_many_posts(self, step_duration):
		try:
			return ceil(step_duration * self.frequency_of_posting())
		except ZeroDivisionError:
			return 0

	def step(self, model):
		number_of_posts = self.how_many_posts(model.step_duration)
		logging.info('User %s should write %d posts', self.name, number_of_posts)
		# print('User %s should write %d posts' % (self.name, number_of_posts))
		# TODO: inserting posts