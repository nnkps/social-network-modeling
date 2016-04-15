from sqlalchemy import Sequence, Column, Integer, String, BigInteger,\
					   DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Author(Base):
	__tablename__ = 'authors'

	id = Column(Integer, Sequence('authors_id_seq'), primary_key=True)
	link = Column(String(255))
	name = Column(String(255))
	facebook_id = Column(BigInteger)

	posts = relationship('Post', back_populates='author')

	def __repr__(self):
		return '<Author(link={}, name={})>'.format(self.link, self.name)


class Category(Base):
	__tablename__ = 'category'
	id = Column(Integer, Sequence('category_id_seq'), primary_key=True)
	category_name = Column(String(200))

	posts = relationship('Post', back_populates='category')

	def __repr__(self):
		return '<Category(category_name={})>'.format(self.category_name)


class Post(Base):
	__tablename__ = 'posts'

	id = Column(Integer, Sequence('posts_id_seq'), primary_key=True)
	date = Column(DateTime)
	link = Column(String(255))
	title = Column(String(255))
	category_id = Column(Integer, ForeignKey('category.id'))
	author_id = Column(Integer, ForeignKey('authors.id'))

	category = relationship('Category', back_populates='posts')
	author = relationship('Author', back_populates='posts')


	def __repr__(self):
		return '<Post(date={}, link={}, title={})>'.format(
			self.date, self.link, self.title)