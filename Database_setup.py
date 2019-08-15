from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Users(Base):
    __tablename__ = "users"
    def __init__(self, **kwargs):
        if 'score' not in kwargs:
             kwargs['score'] = self.__table__.c.money.default.arg
        super(Users, self).__init__(**kwargs)
    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False, unique=True)
    score = Column(Integer, default=0)
    ext = Column(String(10), default="xzy")


engine = create_engine("sqlite:///storeitemes.db")
Base.metadata.create_all(engine)
