import logging
import datetime

from mesa import Model
from mesa.time import RandomActivation

from .agents import UserAgent
from db.objects import Post, Comment, Author, Category



class SocialNetworkModel(Model):
	"""A model of social network with some user agents"""

	def _choose_max_date(self, posts):
		return sorted(posts, key=lambda post: post.date, reverse=True)[0].date

	@property
	def current_date(self):
		return self.start_date + datetime.timedelta(days=self.number_of_steps * self.step_duration)

	def __init__(self, session, step_duration, step_count, commenting_options, verbose=True):
		self.running = True
		self.schedule = RandomActivation(self)
		self.session = session
		self.verbose = verbose

		self.step_duration = step_duration
		self.step_count = step_count
		self.commenting_options = commenting_options

		# these don't change
		self.authors = self.session.query(Author).all()
		self.categories = self.session.query(Category).all()

		# these change after step
		self.posts = self.session.query(Post).all()
		self.comments = self.session.query(Comment).all()

		self.number_of_steps = 0
		self.start_date = self._choose_max_date(self.posts) + datetime.timedelta(days=1)

		if self.verbose:
			logging.info('Beginning of first step {}'.format(self.start_date))

			logging.info('Initializing SocialNetworkModel with %d posts, %d comments, %d authors and %d categories',
				len(self.posts), len(self.comments), len(self.authors), len(self.categories))

		for author in self.authors:
			user_posts = list(filter(lambda post: post.author_id == author.id, self.posts))
			user_comments = list(filter(lambda comment: comment.author_id == author.id, self.comments))

			if self.verbose:
				logging.info('Adding author with name %s and %d posts and %d comments',
					author.name, len(user_posts), len(user_comments))

			user = UserAgent(author.id, author.name, author, user_posts, user_comments)
			self.schedule.add(user)

	def step(self):
		'''Advance the model by one step'''
		self.schedule.step()
		self.number_of_steps += 1

	def run_model(self, step_count=200):
		'''Run model steps'''
		for i in range(step_count):
			if self.verbose:
				logging.info('Executing %d step', i)

			self.step()
			self.session.commit()

			self.posts = self.session.query(Post).all()
			self.comments = self.session.query(Comment).all()
