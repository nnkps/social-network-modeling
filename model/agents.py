from mesa import Agent
from math import ceil
from functools import reduce
import random

import logging


class UserAgent(Agent):
	"""An agent with user behavior"""
	def __init__(self, unique_id, name, posts, comments):
		self.unique_id = unique_id
		self.name = name
		self.posts = posts
		self.comments = comments

	def sorted_categories(self):
		def count_categories(categories, post):
			category_id = post.category_id
			categories[category_id] = categories.get(category_id, 0) + 1
			return categories

		category_count = reduce(count_categories, self.posts, {})
		sorted_categories = sorted(list(category_count.items()), key=lambda e: e[1], reverse=True)

		return [item[0] for item in sorted_categories]

	def frequency_of_behaviour(self, behaviour_items):
		behaviour_items.sort(key=lambda comment: comment.date)
		if len(behaviour_items) > 1:
			first, last = behaviour_items[0], behaviour_items[-1]
			return len(behaviour_items) / ((last.date - first.date).days + 1)
		return 0

	def number_of_posts(self, step_duration, frequency):
		PROBABILIY = 0.8
		DELTA = 5

		try:
			count = ceil(step_duration * frequency)
			distortion = 0

			if random.random() > PROBABILIY:
				distortion = random.randrange(-DELTA, DELTA, 1)

			if count + distortion < 0:
				return 0
			return count + distortion 
		except ZeroDivisionError:
			return 0

	def step(self, model):
		# number_of_posts = self.how_many_posts(model.step_duration)
		# logging.info('User %s should write %d posts', self.name, number_of_posts)
		top_categories = self.sorted_categories()[:3]
		user_comments = self.comments
		# logging.info('User {} has comments {}'.format(self.name, user_comments))
		logging.info('User {} has favourite categories {}'.format(self.name, top_categories))
		logging.info('User {} should post={}'.format(
			self.name,
			self.number_of_posts(model.step_duration, self.frequency_of_behaviour(self.posts))))
		# TODO: inserting posts
