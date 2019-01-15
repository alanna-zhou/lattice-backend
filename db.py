from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
db = SQLAlchemy()

user_to_group = db.Table('user_to_group', 
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'))
)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    groups = db.relationship('Group', secondary=user_to_group, backref=db.backref('members', lazy='dynamic'))

    def __init__(self, **kwargs):
      self.username = kwargs.get('username')
      self.name = kwargs.get('name')
    
    def serialize(self):
      return {
          'username': self.username,
          'name': self.name,
      }

class Match(db.Model):
    __tablename__ = 'match'
    id = db.Column(db.Integer, primary_key=True)
    first_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    second_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    first_user = db.relationship("User", foreign_keys=[first_user_id])
    second_user = db.relationship("User", foreign_keys=[second_user_id])
 
    def __init__(self, **kwargs):
      self.first_user_id = kwargs.get('first_user_id')
      self.second_user_id = kwargs.get('second_user_id')
    
    def serialize(self):
      if self.first_user is not None and self.second_user is not None:
        return {
            'first_username': self.first_user.username,
            'second_username': self.second_user.username,
        }
      return None

class Event(db.Model):
    __tablename__ = 'event'
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String, nullable=False)
    start_date = db.Column(db.String, nullable=False)
    end_date = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    is_private = db.Column(db.Boolean, nullable=False)
    user_to_event = db.relationship('UserToEvent', cascade='delete')

    def __init__(self, **kwargs):
      self.event_name = kwargs.get('event_name')
      self.start_date = kwargs.get('start_date')
      self.end_date = kwargs.get('end_date')
      self.location = kwargs.get('location')
      self.is_private = kwargs.get('is_private')

    def serialize(self):
      return {
          'id': self.id,
          'event_name': self.event_name,
          'start_date': self.start_date,
          'end_date': self.end_date,
          'location': self.location,
          'is_private': self.is_private,
      }

class UserToEvent(db.Model):
    __tablename__ = 'usertoevent'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)

    def __init__(self, **kwargs):
      self.user_id = kwargs.get('user_id')
      self.event_id = kwargs.get('event_id')
    
    def serialize(self):
      return {
          'user_id': self.user_id,
          'event_id': self.event_id,
      }

class Group(db.Model):
    __tablename__ = 'group'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    
    def __init__(self, **kwargs):
      self.name = kwargs.get('name')
    
    def serialize(self):
      group_members = []
      print('self.members', self.members)
      if self.members.all() is not None:
        for member in self.members.all():
          print('member: ', member.serialize())
          group_members.append(member.username)
      return {
          'group_id': self.id,
          'group_name': self.name,
          'group_members': group_members,
      }



# groupname.members.append(user)