from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class TestResult(Base):
    __tablename__ = 'test_results'

    user_id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    score = Column(Integer)


engine = create_engine('sqlite:///test_results.db', echo=True)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()