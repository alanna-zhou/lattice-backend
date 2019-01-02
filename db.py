from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)

    def __init__(self, **kwargs):
      self.username = kwargs.get('username')
      self.name = kwargs.get('name')
    
    def serialize(self):
      return {
          'username': self.username,
          'name': self.name
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
            'second_username': self.second_user.username
        }
      return None