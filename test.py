# coding=utf-8

from datetime import datetime
import app.utils
from app.utils import apis, config
from flask import Flask, current_app, jsonify
from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask.ext.sqlalchemy import SQLAlchemy

from app import db, create_app

class BaseModel():
    @classmethod
    def add(self, resource):
        db.session.add(resource)
        return db.session.commit()

    @classmethod
    def update(self):
        return db.session.commit()

    @classmethod
    def delete(self, resource):
        db.session.delete(resource)
        return db.session.commit()

    @classmethod
    def timestamp2datetime(self, tsp):
        return datetime.fromtimestamp(tsp).strftime('%Y-%m-%d %H:%M:%S')


class UserTest():
    def __init__(self, name):
        self.name = name

    @classmethod
    def update_class(cls, name):
        cls.name = name

    @staticmethod
    def update_static(name):
        print name


if __name__ == '__main__':
    pass