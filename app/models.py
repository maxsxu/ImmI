from datetime import datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from markdown import markdown
import bleach
from flask import current_app, request, url_for
from flask.ext.login import UserMixin, AnonymousUserMixin, current_user
from app.exceptions import ValidationError
from . import db, login_manager


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


class User(UserMixin, BaseModel, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.BigInteger, primary_key=True)
    email = db.Column(db.String(64), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    username = db.Column(db.String(64), nullable=True)
    nickname = db.Column(db.String(64), nullable=True)
    youdao_id = db.Column(db.String(64), nullable=False, unique=True)
    youdao_used_size = db.Column(db.Integer, nullable=True)
    youdao_total_size = db.Column(db.Integer, nullable=True)
    youdao_register_time = db.Column(db.DateTime, nullable=True)
    youdao_last_login_time = db.Column(db.DateTime, nullable=True)
    oauth_token = db.Column(db.String, nullable=True)
    confirmed = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    # notebooks = db.relationship("Notebook", foreign_keys=[Notebook.id], lazy='dynamic')
    # notes = db.relationship("Note", foreign_keys=[Note.id], lazy='dynamic')

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(**kwargs)

        if args:  # position args
            if len(args) == 1:  # only one data passed
                if isinstance(args[0], dict):
                    self.update_with_json(args[0])
        if kwargs:  # keywords args
            for arg in kwargs:
                if isinstance(kwargs[arg], dict):
                    self.update_with_json(kwargs[arg])
                else:
                    if arg == "password":
                        self.password = generate_password_hash(kwargs[arg])
                    else:
                        self.__dict__[arg] = kwargs[arg]

    def update_with_json(self, yuser):
        data = yuser
        if isinstance(data, dict):
            self.nickname = data['user']
            self.youdao_id = data["id"]
            self.youdao_register_time = self.timestamp2datetime(data["register_time"] / 1000)
            self.youdao_last_login_time = self.timestamp2datetime(data["last_login_time"] / 1000)
            self.youdao_total_size = data["total_size"]
            self.youdao_used_size = data["used_size"]
            self.oauth_token = data["oauth_token"]
        return self

    def verify_password(self, pd):
        return check_password_hash(self.password, pd)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        self.update()
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True

    def can(self, permissions):
        return True

    def is_administrator(self):
        return True

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def toJSON(self):
        json_user = {
            'id': self.id,
            'email': self.email,
            'password': self.password,
            'username': self.username,
            'youdao_id': self.youdao_id,
            'nickname': self.nickname,
            'member_since': self.member_since,
            'last_seen': self.last_seen,
        }
        return json_user

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id}).decode('ascii')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def __repr__(self):
        return '<User %r>' % self.youdao_id


class NotebookGroup():
    def __init__(self, name, count, notebooks):
        self.groupName = name
        self.notebookCount = count
        self.notebooks = notebooks

    def addNotebook(self, notebook):
        if isinstance(notebook, Notebook):
            self.notebooks.append(notebook)
        elif isinstance(notebook, list):
            self.notebooks.extend(notebook)


class Notebook(BaseModel, db.Model):
    __tablename__ = 'notebook'

    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.Text, nullable=False)
    name = db.Column(db.String)
    notes_num = db.Column(db.Integer)
    group = db.Column(db.String)
    create_time = db.Column(db.DateTime)
    modify_time = db.Column(db.DateTime)
    user_youdao_id = db.Column(db.Integer, db.ForeignKey('user.youdao_id'), index=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id'), index=True)

    def __init__(self, *args, **kwargs):
        super(Notebook, self).__init__(**kwargs)

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

    def update_with_json(self, ynotebooks):
        data = ynotebooks
        if isinstance(data, dict):
            self.path = data["path"]
            self.name = data["name"]
            self.notes_num = data["notes_num"]
            self.group = data["group"]
            self.create_time = self.timestamp2datetime(data["create_time"])
            self.modify_time = self.timestamp2datetime(data["modify_time"])
            self.user_youdao_id = current_user.youdao_id
            self.user_id = current_user.id

    @classmethod
    def getNotebookGroup(self):
        notebookGroups = []
        groups = db.session.query(Notebook.group, db.func.count().label("count")) \
            .filter(Notebook.user_id == current_user.id).group_by(Notebook.group).order_by('count').all()
        for group in groups:
            groupName = group[0]
            notebookCount = group[1]
            nbs = Notebook.query.filter_by(group=groupName).all()
            nbg = NotebookGroup(groupName, notebookCount, nbs)
            notebookGroups.append(nbg)
        return notebookGroups


class Note(BaseModel, db.Model):
    __tablename__ = 'note'

    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.Text)
    title = db.Column(db.String)
    author = db.Column(db.String)
    source = db.Column(db.String)
    thumbnail = db.Column(db.String)
    size = db.Column(db.Integer)
    content = db.Column(db.Text)
    create_time = db.Column(db.DateTime)
    modify_time = db.Column(db.DateTime)
    notebook_id = db.Column(db.Integer, db.ForeignKey("notebook.id"), index=True)
    user_youdao_id = db.Column(db.Integer, db.ForeignKey('user.youdao_id'), index=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id'), index=True)
    images = []

    def __init__(self, *args, **kwargs):
        super(Note, self).__init__(**kwargs)

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

    def update_with_json(self, ynote):
        data = ynote
        if isinstance(data, dict):
            self.path = data["path"]
            self.title = data["title"]
            self.author = data["author"]
            self.thumbnail = data["thumbnail"]
            self.source = data["source"]
            self.size = data["size"]
            self.content = data["content"]
            self.create_time = self.timestamp2datetime(data["create_time"])
            self.modify_time = self.timestamp2datetime(data["modify_time"])
            self.user_youdao_id = current_user.youdao_id
            self.user_id = current_user.id

    def addImage(self, image):
        return self.images.append(image)

    def toJSON(self):
        return {
            "id": self.id,
            "title": self.title,
            "size": self.size
        }

class Image(BaseModel, db.Model):
    ''' the images in note '''
    __tablename__ = 'image'

    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.Text, nullable=False)
    note_id = db.Column(db.Integer, db.ForeignKey("note.id"), index=True)

    def __init__(self, *args, **kwargs):
        super(Image, self).__init__(**kwargs)

        if kwargs:  # keywords args
            for arg in kwargs:
                self.__dict__[arg] = kwargs[arg]


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


if __name__ == '__main__':
    ydate = {
        "id": "ac617c806cba1e1baba43e1677b8007d5bb72ea7",
        "register_time": 1369500863816,
        "used_size": 43605401,
        "last_login_time": 1460900356183,
        "total_size": 8336548864,
        "last_modify_time": 1460769948960,
        "default_notebook": "/SVRD0EB13333CD44EA3A9582892481F1D96",
        "user": "m13***"
    }
    u = User(id=1)
    print u.toJSON()
    u.update_with_json(ydate)
    print u.toJSON()
