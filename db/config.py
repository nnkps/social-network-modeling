from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from . import credentials

engine = create_engine('postgresql://{}:{}@{}:{}/{}'.format(
	credentials.USER,
	credentials.PASSWORD,
	credentials.HOST,
	credentials.PORT,
	credentials.DATABASE))

Session = sessionmaker(bind=engine)
