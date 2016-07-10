from sqlalchemy import Sequence, Column, Integer, String, BigInteger,\
					   DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Author(Base):
	__tablename__ = 'authors'

	id = Column(Integer, Sequence('authors_id_seq'), primary_key=True)
	name = Column(String(255))
	# facebook_id = Column(BigInteger)

	posts = relationship('Post', back_populates='author')
	comments = relationship('Comment', back_populates='author')

	def __repr__(self):
		return '<Author(name={})>'.format(self.name)


class Category(Base):
	__tablename__ = 'category'
	id = Column(Integer, Sequence('category_id_seq'), primary_key=True)
	category_name = Column(String(200))

	posts = relationship('Post', back_populates='category')

	def __repr__(self):
		return '<Category(category_name={})>'.format(self.category_name)


class Post(Base):
	__tablename__ = 'posts'

	id = Column(Integer, Sequence('posts_id_seq'), primary_key=True, nullable=False)
	date = Column(DateTime)
	category_id = Column(Integer, ForeignKey('category.id'), index=True)
	author_id = Column(Integer, ForeignKey('authors.id'), index=True)

	category = relationship('Category', back_populates='posts')
	author = relationship('Author', back_populates='posts')
	comments = relationship('Comment', back_populates='post')

	def __repr__(self):
		return '<Post(id={}, date={}, author_id={}, category_id={})>'.format(
			self.id,
			self.date,
			self.author_id,
			self.category_id)


class Comment(Base):
	__tablename__ = 'comments'

	id = Column(Integer, Sequence('comments_id_seq'), primary_key=True, nullable=False)
	date = Column(DateTime)
	author_id = Column(Integer, ForeignKey('authors.id'))
	post_id = Column(Integer, ForeignKey('posts.id'))

	author = relationship('Author', back_populates='comments')
	post = relationship('Post', back_populates='comments')

	def __repr__(self):
		return '<Comment(id={}, date={}, author_id={}, post_id={})>'.format(
			self.id,
			self.date,
			self.author_id,
			self.post_id)
