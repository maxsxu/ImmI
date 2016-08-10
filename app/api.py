# coding=utf-8

import requests
import re
from flask import request, session
from flask.ext.login import current_user
from app.utils import config, apis


class Api(object):
    def __init__(self):
        self.oauth_token = None

    def init_app(self, app):
        self.app = app
        self.request = request
        self.session = session

    def setOauthToken(self):
        try:
            for api in apis:
                if self.oauth_token: break
                if not session.has_key("oauth_token"):
                    from app.models import User
                    oauth_token = User.query.get(current_user.id).oauth_token
                    session["oauth_token"] = oauth_token
                apis[api]["params"]["oauth_token"] = session["oauth_token"] or request.cookies.get('oauth_token', '')
            self.oauth_token = session["oauth_token"]
            return True
        except Exception as e:
            return False

    def authorize(self):
        responses = requests.get(
            url=apis["authorize"]["url"],
            params=apis["authorize"]["params"]
        )
        responses = responses.text
        return responses

    def accessToken(self, code):
        apis["access_token"]["params"]["code"] = code
        responses = requests.get(
            url=apis["access_token"]["url"],
            params=apis["access_token"]["params"]
        )
        responses = responses.json()
        try:
            return responses["accessToken"]
        except KeyError as e:
            return None

    def getUser(self):
        responses = requests.get(
            url=apis["get_user"]["url"],
            params=apis["get_user"]["params"]
        )
        user = responses.json()
        return user

    def getNotebooks(self):
        responses = requests.post(
            url=apis["get_notebooks"]["url"],
            params=apis["get_notebooks"]["params"],
            verify=True
        )
        return responses.json()

    def getNotesPath(self, notebook):
        apis["get_notes_path"]["data"]["notebook"] = notebook
        responses = requests.post(
            url=apis["get_notes_path"]["url"],
            data=apis["get_notes_path"]["data"],
            params=apis["get_notes_path"]["params"],
            verify=True
        )
        return responses.json()

    def getNote(self, path):
        apis["get_note"]["data"]["path"] = path
        responses = requests.post(
            url=apis["get_note"]["url"],
            data=apis["get_note"]["data"],
            params=apis["get_note"]["params"],
            verify=True
        )
        return responses.json()


    def getImage(self, url):
        apis["get_image"]["url"] = url
        responses = requests.get(
            url=apis["get_image"]["url"],
            params=apis["get_image"]["params"],
            verify=True
        )
        type = responses.headers["Content-Type"][6:]
        p = re.compile("(\:|\/\/|\.|\/)")
        imageName = p.sub("", url)+"."+type
        with open("images/" + imageName, 'wb') as img:
            img.write(responses.content)
        return imageName

if __name__ == '__main__':
    pass
