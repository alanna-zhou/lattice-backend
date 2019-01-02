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