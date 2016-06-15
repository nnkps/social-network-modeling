from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from . import credentials

ro_engine = create_engine('postgresql://{}:{}@{}:{}/{}'.format(
	credentials.USER,
	credentials.PASSWORD,
	credentials.HOST,
	credentials.PORT,
	credentials.DATABASE))

ROSession = sessionmaker(bind=ro_engine)

rw_engine = create_engine('sqlite:///foo.db')

RWSession = sessionmaker(bind=rw_engine)
