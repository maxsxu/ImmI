from flask import render_template, redirect, url_for, abort, flash, request, \
    current_app, make_response, jsonify, session
from flask.ext.login import login_required, current_user, login_user
from flask.ext.sqlalchemy import get_debug_queries
from . import main
from .forms import EditProfileForm, PostForm, CommentForm
from .. import db
from ..models import User, Notebook, Note, NotebookGroup
from ..decorators import admin_required, permission_required
from oauth import OAuthSignIn
from .. import YoudaoApi
from bs4 import BeautifulSoup


@main.before_request
def before_request():
    if current_user.is_authenticated and not YoudaoApi.setOauthToken():
        abort(403)
    print request.host, request.headers["Host"]


@main.route('/authorize/<service>')
def oauth_authorize(service):
    oauth = OAuthSignIn.get_service(service)
    return oauth.authorize()


@main.route('/callback/<service>')
def oauth_callback(service):
    oauth = OAuthSignIn.get_service(service)
    youdao_user = oauth.callback()

    if youdao_user is None:
        flash('Authentication failed.')
        return redirect(url_for('main.index'))

    user = User.query.filter_by(youdao_id=youdao_user['id']).first()
    if not user:
        user = User.query.get(current_user.id)
        user.update_with_json(youdao_user)
        user.update()
    login_user(user, True)
    response = make_response(redirect(url_for('main.index')))
    response.set_cookie("oauth_token", user.oauth_token)
    YoudaoApi.setOauthToken()
    return response


@main.route("/index")
@main.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        notebookGroups = Notebook.getNotebookGroup()
        notebooksLoaded = True and (len(notebookGroups) != 0)

        return render_template('index.html',
                               notebookGroups=notebookGroups, notebooksLoaded=notebooksLoaded)
    else:
        return render_template('index.html')


@main.route("/start")
@login_required
def start():
    notebooks = YoudaoApi.getNotebooks()
    for nb in notebooks:
        notebook = Notebook(nb)
        Notebook.add(notebook)

    return redirect(url_for('main.index'))


@main.route("/notebook/<int:notebook_id>")
@login_required
def showNotebook(notebook_id):
    notebook = Notebook.query.get(notebook_id)
    notes = []
    notePaths = YoudaoApi.getNotesPath(notebook.path)
    for np in notePaths:
        nt = YoudaoApi.getNote(np)
        note = Note.query.filter_by(path=nt['path']).first()
        if note:
            notes.append(note)
            continue

        note = Note(nt)
        note.notebook_id = notebook_id

        # conten handling
        content = note.content
        soup = BeautifulSoup(content)
        imags = soup.findAll('img', {'data-media-type':'image'})
        for img in imags:
            imgUrl = img["src"]
            print(imgUrl)
            imgName = YoudaoApi.getImage(imgUrl)
            img["src"] = "images/"+imgName
        note.content = str(soup)

        Note.add(note)
        notes.append(note)
    return render_template("index.html", notebook=notebook, notes=notes, showNote=True)


@main.route("/download")
@login_required
def download():
    notes = list(Note.query.all())
    return jsonify({"notes": [note.toJSON() for note in notes]})