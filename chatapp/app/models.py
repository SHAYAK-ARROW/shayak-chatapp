from flask_sqlalchemy import SQLAlchemy
import datetime

# data base obj toiri
db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # full name
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(50), nullable=False)  # who send
    receiver = db.Column(db.String(50), nullable=False)  # to whom (username, "General" or "group_<id>")
    content = db.Column(db.String(500), nullable=False)  # sms
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    creator = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class GroupMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(50), nullable=False)


class ReadStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    room = db.Column(db.String(120), nullable=False)
    last_read = db.Column(db.DateTime, default=datetime.datetime.utcnow)
