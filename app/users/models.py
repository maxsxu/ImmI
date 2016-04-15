# coding=utf-8

from flask.ext.login import UserMixin
from app import db, BaseModel


class User(db.Model, UserMixin, BaseModel):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), nullable=False, unique=True)
    password = db.Column(db.String(64), nullable=False)
    username = db.Column(db.String(64), nullable=True)
    nickname = db.Column(db.String(64), nullable=True)
    youdao_id = db.Column(db.String(64), nullable=False, unique=True)
    youdao_used_size = db.Column(db.Integer, nullable=True)
    youdao_total_size = db.Column(db.Integer, nullable=True)
    youdao_register_time = db.Column(db.DateTime, nullable=True)
    youdao_last_login_time = db.Column(db.DateTime, nullable=True)
    oauth_token = db.Column(db.String, nullable=True)

    def __init__(self, *args, **kwargs):
        if args:  # position args
            if len(args) == 1:  # only one data passed
                if isinstance(args[0], dict):
                    self.update_with_json(args[0])
        if kwargs:  # keywords args
            for arg in kwargs:
                if isinstance(kwargs[arg], dict):
                    self.update_with_json(kwargs[arg])
                else:
                    self.__dict__[arg] = kwargs[arg]

    @classmethod
    def update_with_json(self, yuser):
        data = yuser
        if isinstance(data, dict):
            self.nickname = data['user']
            self.youdao_id = data["id"]
            self.youdao_register_time = data["register_time"]
            self.youdao_last_login_time = data["last_login_time"]
            self.youdao_total_size = data["total_size"]
            self.youdao_used_size = data["used_size"]
            self.oauth_token = data["oauth_token"]

    def __repr__(self):
        return '<User %r>' % self.youdao_id


if __name__ == '__main__':
    pass
