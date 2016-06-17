import logging
from functools import reduce
from math import ceil
import random
import datetime

from mesa import Agent

from db.objects import Post, Comment


class UserAgent(Agent):
	"""An agent with user behavior"""
	def __init__(self, unique_id, name, user, posts, comments):
		self.unique_id = unique_id
		self.name = name
		self.user = user
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

	def number_of_posts(self, step_duration, frequency):
		PROBABILIY = 0.8
		DELTA = 2

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
		propability_of_writing_post = 0.5
		propability_of_commenting = 0.6
		period = model.step_duration * 1  # TODO: should be in settings
		age_of_post = model.step_duration * 1.4

		def is_recent(item):
			return item.date > model.current_date - datetime.timedelta(days=period)

		if model.verbose:
			logging.info('User {} wrote {} posts and {} comments'
				.format(self.name, len(self.posts), len(self.comments)))

		# writing posts
		if random.random() > propability_of_writing_post:
			for category in model.categories:
				recent_posts = filter(is_recent, self.posts)
				recent_posts_in_category = list(filter(lambda post: post.category_id == category.id, recent_posts))

				frequency_of_posting = len(recent_posts_in_category) / period
				predicted_number_of_posts = self.number_of_posts(model.step_duration, frequency_of_posting)

				for i in range(predicted_number_of_posts):
					new_post = Post(author=self.user,
									category=category,
									date=model.current_date)
					
					model.session.add(new_post)
					self.posts.append(new_post)
		
		authors_count = len(model.authors)

		def is_not_old(post):
			return post.date > model.current_date - datetime.timedelta(days=age_of_post)

		# writing comments
		if random.random() > propability_of_commenting:
			for post in filter(is_not_old, model.posts):
				post_comments = post.comments
				user_comments = list(filter(lambda comment: comment.author_id == self.unique_id,
									   		post_comments))

				predicted_number_of_comments = 0
				
				if len(user_comments) > 0:
					# user already commented this post
					# TODO: consider date of post, if it's old then it's not commented anymore
					recent_user_comments_for_post = list(filter(is_recent, user_comments)) 
					frequency_of_commenting = len(recent_user_comments_for_post) / period
				else:
					recent_user_comments = filter(is_recent, self.comments)

					recent_user_comments_for_category = list(filter(lambda comment: comment.post.category_id == post.category_id,
													   		 		recent_user_comments))
					frequency_for_category = len(recent_user_comments_for_category) / period
					
					recent_user_comments_for_author = list(filter(lambda comment: comment.post.author_id == post.author_id,
														   		  recent_user_comments))
					frequency_for_author = len(recent_user_comments_for_author) / period

					# average number of comments per user?
					recent_post_comments = list(filter(is_recent, post_comments))
					recent_comments_count = ceil(len(recent_post_comments) / authors_count)
					frequency_for_popularity = recent_comments_count / period

					author_weight = model.commenting_options['weights']['author']
					category_weight = model.commenting_options['weights']['category']
					popularity_weight = model.commenting_options['weights']['popularity']

					frequency_of_commenting = (frequency_for_category * category_weight + \
						frequency_for_author * author_weight + \
						frequency_for_popularity * popularity_weight) / (author_weight + category_weight + popularity_weight)

				frequency_of_commenting /= (model.current_date - post.date).days**4
				predicted_number_of_comments = self.number_of_posts(model.step_duration, frequency_of_commenting)

				for i in range(predicted_number_of_comments):
					new_comment = Comment(author=self.user,
										  post=post,
										  date=model.current_date)

					model.session.add(new_comment)
					self.comments.append(new_comment)

				

