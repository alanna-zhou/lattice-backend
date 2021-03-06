import json
import requests
from db import db, User, Match, Event, UserToEvent, Group, user_to_group
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

def validate_json(post_body, fields):
  """Checks that the post body contains every element in the list of fields. If all fields are found, method returns None."""
  for f in fields:
    if f not in post_body:
      return json.dumps({'success': False, 'error': 'Missing this necessary parameter: {}'.format(f)}), 404
  return None

def validate_objects(objects):
  """Checks if the list of objects are none. Returns None if they are all valid objects."""
  for o in objects:
    if o is None:
      return json.dumps({'success': False, 'error': 'Parameter(s) is invalid!'}), 404
  return None

@app.route('/api/user/', methods=['POST'])
def create_user():
  post_body = json.loads(request.data)
  v = validate_json(post_body, ['username', 'name'])
  if v is not None:
    return v
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
  v = validate_objects([user])
  if v is not None:
    return v
  return json.dumps({'success': True, 'data': user.serialize()}), 200

@app.route('/api/user/<string:username>/', methods=['DELETE'])
def delete_user(username):
  user = User.query.filter_by(username=username).first()
  v = validate_objects([user])
  if v is not None:
    return v
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

@app.route('/api/match/', methods=['POST'])
def match_users():
  post_body = json.loads(request.data)
  v = validate_json(post_body, ['first_username', 'second_username'])
  if v is not None:
    return v
  first_user = User.query.filter_by(username=post_body.get('first_username')).first()
  second_user = User.query.filter_by(username=post_body.get('second_username')).first()
  v = validate_objects([first_user, second_user])
  if v is not None:
    return v
  match = Match.query.filter_by(first_user_id=first_user.id, second_user_id=second_user.id).first()
  if match is not None:
    return json.dumps({'success': False, 'error': 'Match already exists!'}), 404
  match = Match(
    first_user_id=first_user.id,
    second_user_id=second_user.id
  )
  db.session.add(match)
  db.session.commit()
  return json.dumps({'success': True, 'data': match.serialize()}), 200

@app.route('/api/match/delete/', methods=['POST'])
def delete_match():
  post_body = json.loads(request.data)
  v = validate_json(post_body, ['first_username', 'second_username'])
  if v is not None:
    return v
  first_user = User.query.filter_by(username=post_body.get('first_username')).first()
  second_user = User.query.filter_by(username=post_body.get('second_username')).first()
  v = validate_objects([first_user, second_user])
  if v is not None:
    return v
  match = Match.query.filter_by(first_user_id=first_user.id, second_user_id=second_user.id).first()
  if match is None:
    return json.dumps({'success': False, 'error': 'Could not delete match. Match is invalid!'}), 404
  db.session.delete(match)
  db.session.commit()
  return json.dumps({'success': True, 'data': match.serialize()}), 200

@app.route('/api/matches/', methods=['GET'])
def get_all_matches():
  query = Match.query.all()
  matches = []
  for m in query:
    if m.serialize() is not None:
      matches.append(m.serialize())
  return json.dumps({'success': True, 'data': matches}), 200

@app.route('/api/event/', methods=['POST'])
def create_event():
  post_body = json.loads(request.data)
  v = validate_json(post_body, ['username', 'start_date', 'end_date'])
  if v is not None:
    return v
  user = User.query.filter_by(username=post_body.get('username')).first()
  v = validate_objects([user])
  if v is not None:
    return v
  event = Event(
    event_name=post_body.get('event_name', ''),
    start_date=post_body.get('start_date'),
    end_date=post_body.get('end_date'),
    location=post_body.get('location', ''),
    is_private=post_body.get('is_private', False),
  )
  db.session.add(event)
  db.session.flush()
  user_to_event = UserToEvent(
    user_id=user.id,
    event_id=event.id
  )
  db.session.add(user_to_event)
  db.session.commit()
  return json.dumps({'success': True, 'data': event.serialize()}), 200

@app.route('/api/events/', methods=['GET'])
def get_all_events():
  usertoevents = UserToEvent.query.all()
  events = []
  for ue in usertoevents:
    user = User.query.filter_by(id=ue.user_id).first()
    event = Event.query.filter_by(id=ue.event_id).first()
    result = {
      'username' : user.username
    }
    result.update(event.serialize())
    events.append(result)
  return json.dumps({'success': True, 'data': events}), 200

@app.route('/api/event/<int:event_id>/', methods=['DELETE'])
def delete_event(event_id):
  event = Event.query.filter_by(id=event_id).first()
  v = validate_objects([event])
  if v is not None:
    return v
  usertoevent = UserToEvent.query.filter_by(event_id=event.id).first()
  v = validate_objects([usertoevent])
  if v is not None:
    return v
  user = User.query.filter_by(id=usertoevent.user_id).first()
  db.session.delete(event)
  db.session.delete(usertoevent)
  db.session.commit()
  result = {
    'username' : user.username,
    'event_id' : event.id
  }
  return json.dumps({'success': True, 'data': result}), 200

@app.route('/api/user/<string:username>/events/', methods=['GET'])
def get_user_events(username):
  user = User.query.filter_by(username=username).first()
  usertoevents = UserToEvent.query.filter_by(user_id=user.id)
  v = validate_objects([user, usertoevents])
  if v is not None:
    return v
  events = []
  for ue in usertoevents:
    events.append(Event.query.filter_by(id=ue.event_id).first().serialize())
  return json.dumps({'success': True, 'data': events}), 200

@app.route('/api/user/<string:username>/events/', methods=['DELETE'])
def delete_user_events(username):
  user = User.query.filter_by(username=username).first()
  usertoevents = UserToEvent.query.filter_by(user_id=user.id)
  v = validate_objects([user, usertoevents])
  if v is not None:
    return v
  deleted_event_ids = [] 
  try: 
    for ue in usertoevents:
      deleted_event_ids.append(ue.event_id)
      db.session.delete(Event.query.filter_by(id=ue.event_id).first())
      db.session.delete(ue)
    db.session.commit()
  except Exception as e:
    print(e)
  result = {
    'username' : user.username,
    'event_ids' : deleted_event_ids
  }
  return json.dumps({'success': True, 'data': result}), 200

@app.route('/api/group/', methods=['POST'])
def create_group():
  try: 
    post_body = json.loads(request.data)
    v = validate_json(post_body, ['group_members'])
    if v is not None:
      return v
    # name and is_private are optional for now?
    group = Group(
      name=post_body.get('group_name', '')
    )
    db.session.add(group)
    db.session.flush()
    print('group: ', group.serialize())
    group_members = post_body.get('group_members')
    print('group_members: ', group_members)
    users = [] 
    for member in group_members:
      user = User.query.filter_by(username=member).first()
      print('user: ', user.serialize())
      print('association table: ', group.members)
      if user is None:
        continue
      group.members.all().append(user)
    db.session.flush()
    result = group.serialize()
    for member in group.members.all():
      print('member serialize', member.serialize())
      print('REACHES HERE?')
      result.append(member.username)
      db.session.commit()
    usernames = [u.username for u in group.members.all()]
    print('usernames', usernames)
    return json.dumps({'success': True, 'data': result}), 200
  except Exception as e:
    print(e)
  return json.dumps({'success': False, 'error': 'haha something went wrong'}), 404

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)