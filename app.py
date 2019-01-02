import json
import requests
from db import db, User
from flask import Flask, request
from sqlalchemy.event import listen
from sqlalchemy import event
from flask_sqlalchemy import SQLAlchemy

db_filename = "data.db"
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % db_filename
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

db.init_app(app)
with app.app_context():
  db.create_all()

@app.route('/api/user/', methods=['POST'])
def create_user():
  post_body = json.loads(request.data)
  if 'username' not in post_body:
    return json.dumps({'success': False, 'error': 'Missing username field!'}), 404
  if 'name' not in post_body:
    return json.dumps({'success': False, 'error': 'Missing name field!'}), 404
  user = User.query.filter_by(username=post_body.get('username')).first()
  if user is not None:
    user.name = post_body.get('name')
    db.session.commit()
    return json.dumps({'success': True, 'data': user.serialize()}), 200
  user = User(
      username=post_body.get('username'), 
      name=post_body.get('name', '')
  )
  db.session.add(user)
  db.session.commit()
  return json.dumps({'success': True, 'data': user.serialize()}), 200

@app.route('/api/user/<string:username>/', methods=['GET'])
def get_user(username):
  user = User.query.filter_by(username=username).first()
  if user is None:
    return json.dumps({'success': False, 'error': 'User does not exist!'}), 404
  return json.dumps({'success': True, 'data': user.serialize()}), 200

@app.route('/api/user/<string:username>/', methods=['DELETE'])
def delete_user(username):
  user = User.query.filter_by(username=username).first()
  if user is None:
    return json.dumps({'success': False, 'error': 'User does not exist!'}), 404
  db.session.delete(user)
  db.session.commit()
  return json.dumps({'success': True, 'data': user.serialize()}), 200

@app.route('/api/users/', methods=['DELETE'])
def delete_all_users():
  user = User.query.all()
  for u in user:
    db.session.delete(u)
    db.session.commit()
  return json.dumps({'success': True}), 200

@app.route('/api/users/', methods=['GET'])
def get_all_users():
  query = User.query.all()
  users = []
  for u in query:
    users.append(u.serialize())
  return json.dumps({'success': True, 'data': users}), 200


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)