from mesa import Model
from mesa.time import RandomActivation
from .agents import UserAgent

import logging


class SocialNetworkModel(Model):
	"""A model of social network with some user agents"""
	# TODO: pass more users' data from database to model
	def __init__(self, posts, comments, step_duration):
		self.running = True
		self.schedule = RandomActivation(self)
		self.step_duration = step_duration

		authors = {post.author for post in posts} | {comment.author for comment in comments}

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
