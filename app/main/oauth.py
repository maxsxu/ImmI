# coding=utf-8

from flask import url_for, request, redirect, session
from rauth import OAuth2Service

from app.api import Api
from app.utils import config


class OAuthSignIn(object):
    services = None

    def __init__(self, service_name):
        credentials = config['oauth_credentials'][service_name]
        self.service_name = service_name
        self.client_id = credentials['client_id']
        self.client_secret = credentials['client_secret']
        self.base_url = config["oauth_credentials"]["youdao"]["host"]
        self.authorize_url = config["oauth_credentials"]["youdao"]["authorize_url"]
        self.access_token_url = config["oauth_credentials"]["youdao"]["access_token_url"]

    def authorize(self):
        pass

    def callback(self):
        pass

    def get_redirect_url(self):
        return url_for('oauth_callback', service=self.service_name, _external=True)

    @classmethod
    def get_service(self, service_name):
        if self.services is None:
            self.services = {}
            for service_class in self.__subclasses__():
                service = service_class()
                self.services[service.service_name] = service
        return self.services[service_name]


class YoudaoSignIn(OAuthSignIn):
    def __init__(self):
        super(YoudaoSignIn, self).__init__('youdao')
        self.service = OAuth2Service(
            name='youdao',
            client_id=self.client_id,
            client_secret=self.client_secret,
            authorize_url=self.authorize_url,
            access_token_url=self.access_token_url,
            base_url=self.base_url
        )

    def authorize(self):
        return redirect(self.service.get_authorize_url(
            response_type='code',
            state='state',
            redirect_uri=self.get_redirect_url())
        )

    def callback(self):
        if 'code' not in request.args:
            return None

        code = request.args['code']
        access_token = Api.accessToken(code)
        session["code"] = code
        session["oauth_token"] = access_token

        # oauth_session = self.service.get_auth_session(
        #     method='GET',
        #     data={
        #         'client_id': self.client_id,
        #         'client_secret': self.client_secret,
        #         'code': code,
        #         'grant_type': 'authorization_code',
        #         'redirect_uri': self.get_redirect_url()
        #     }
        # )
        #
        # access_token = oauth_session.access_token
        # me = oauth_session.get('').json()

        if access_token:
            user = Api.getUser(access_token)
            user['oauth_token'] = access_token
            return user
        else:
            return None


if __name__ == '__main__':
    oauth = OAuthSignIn.get_service("youdao")
    oauth_url = oauth.service.get_authorize_url(
        response_type='code',
        state='state',
        redirect_uri="dev.maxthread.com"
    )
    print(oauth_url)
