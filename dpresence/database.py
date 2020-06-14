import uuid
from collections import defaultdict

from sqlalchemy import (create_engine, Column, Integer, Sequence, String,
                        Text, Boolean)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from bottle.ext import sqlalchemy


Base = declarative_base()
engine = create_engine('sqlite:////tmp/presence.db', echo=False)

db_plugin = sqlalchemy.Plugin(engine, Base.metadata, keyword='db',
                              create=True, commit=True, use_kwargs=True)


def get_session():
    return sessionmaker()(bind=engine)



class Application(Base):
    """Defines an application.
    """
    __tablename__ = 'application'

    id = Column(Integer, Sequence('id_seq'), primary_key=True)

    uid = Column(Integer)
    name = Column(String(200))
    description = Column(Text())
    email = Column(String(200))
    domain = Column(String(200))
    notified = Column(Boolean)
    valid_domain = Column(Boolean)
    api_key = Column(String(200))
    domain_key = Column(String(200))

    def __init__(self, **data):
        self.name = data['name']
        self.domain = data['domain']
        self.email = data['email']
        self.description = data.get('description', '')
        self.uid = str(uuid.uuid4())
        self.valid_domain = self.notified = False
        self.generate_apikey()
        self.domain_key = str(uuid.uuid4())

    def generate_apikey(self):
        self.api_key = str(uuid.uuid4())

    def validate_domain(self):
        # XXX here we'll call domain/__presence
        self.valid_domain = True


class ApplicationUser(Base):
    __tablename__ = 'application_user'

    id = Column(Integer, Sequence('id_seq2'), primary_key=True)

    email = Column(String(200))
    appid = Column(String(200))
    uid = Column(Integer)

    def __init__(self, application, email):
        self.appid = application
        self.email = email
        self.uid = str(uuid.uuid4())



_NOTIFICATIONS = defaultdict(list)

def push_notification(notification):
    _NOTIFICATIONS[notification['target']].append(notification)


def pop_notifications(email):
    try:
        return list(_NOTIFICATIONS[email])
    finally:
        _NOTIFICATIONS[email] = []


Base.metadata.create_all(engine, checkfirst=True)
