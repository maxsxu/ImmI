# coding=utf-8

import requests

from app.utils import apis


class Api(object):
    def __init__(self):
        pass

    @staticmethod
    def authorize():
        responses = requests.get(
            url=apis["authorize"]["url"],
            params=apis["authorize"]["params"]
        )
        responses = responses.text
        return responses

    @staticmethod
    def accessToken(code):
        apis["access_token"]["params"]["code"] = code
        responses = requests.get(
            url=apis["access_token"]["url"],
            params=apis["access_token"]["params"]
        )
        responses = responses.json()
        return responses["accessToken"]

    @staticmethod
    def getUser(oauth_token):
        # if oauth_token:
        #     apis["get_user"]["params"]["oauth_token"] = oauth_token
        responses = requests.get(
            url=apis["get_user"]["url"],
            params=apis["get_user"]["params"]
        )
        user = responses.json()
        return user

    @staticmethod
    def getNotebooks():
        responses = requests.post(
            url=apis["get_notebooks"]["url"],
            params=apis["get_notebooks"]["params"]
        )
        return responses.json()

    @staticmethod
    def getNotesPath(notebook):
        apis["get_notes_path"]["data"]["notebook"] = notebook
        responses = requests.post(
            url=apis["get_notes_path"]["url"],
            data=apis["get_notes_path"]["data"],
            params=apis["get_notes_path"]["params"]
        )
        return responses.json()

    @staticmethod
    def getNote(path):
        apis["get_note"]["data"]["path"] = path
        responses = requests.post(
            url=apis["get_note"]["url"],
            data=apis["get_note"]["data"],
            params=apis["get_note"]["params"]
        )
        return responses.json


if __name__ == '__main__':
    print(Api.getNotesPath("/93283ca4083dc3bffdef0030fc0e1bea"))