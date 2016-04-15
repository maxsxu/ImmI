# coding=utf-8

from flask import render_template, request, url_for, redirect, json, flash, make_response
from flask.ext.login import login_user, logout_user, current_user

from app.main import main
from app.users.models import User
from app.main.oauth import OAuthSignIn


@main.before_request
def before_request():
    print request.host, request.headers["Host"]

@main.route('/authorize/<service>')
def oauth_authorize(service):
    oauth = OAuthSignIn.get_service(service)
    return oauth.authorize()


@main.route('/callback/<service>')
def oauth_callback(service):
    oauth = OAuthSignIn.get_service(service)
    youdao_user = oauth.callback()
    if youdao_user['id'] is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    user = User.query.filter_by(youdao_id=youdao_user['id']).first()
    if not user:
        user = User.query.get(current_user.id)
        user.update_with_json(youdao_user)
        user.update()
    login_user(user, True)
    response = make_response(redirect(url_for('index')))
    response.set_cookie("oauth_token", user.oauth_token)
    return response


@main.route('/')
@main.route('/index')
def index():
    render_template(url_for('index'))
    return render_template('index.html')


@main.route('/showSignIn')
def showSignIn():
    return render_template('signin.html')


@main.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')


@main.route('/signOut')
def signOut():
    logout_user()
    return redirect(url_for('index'))


@main.route('/signIn', methods=['POST', 'GET'])
def signIn():
    try:
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        if _email and _password:
            user = User.query.filter_by(email=_email).first()
            if user:
                if user.password == _password:
                    login_user(user, True)
                    return render_template('index.html')
                else:
                    return render_template('signin.html', password=False)
            else:
                return render_template('signin.html', email=False)
    except Exception as e:
        return json.dumps({'error': str(e)})
    finally:
        pass


@main.route('/signUp', methods=['POST', 'GET'])
def signUp():
    try:
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        # validate the received values
        if _name and _email and _password:
            user = User.query.filter_by(email=_email).first()
            if not user:
                user = User(username=_name, email=_email, password=_password)
                User.add(user)
                login_user(user, True)
                return render_template('index.html')
            else:
                return json.dumps({'error' : "user exist"})
        else:
            return json.dumps({'html': '<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'error': str(e)})
    finally:
        pass


if __name__ == '__main__':
    pass