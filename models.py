import datetime

from flask_bcrypt import generate_password_hash
from flask_login import UserMixin
from peewee import *

DATABASE = SqliteDatabase('journals.db')


class User(UserMixin, Model):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField(max_length=100)
    joined_at = DateTimeField(default=datetime.datetime.now)
    is_admin = BooleanField(default=False)

    class Meta:
        database = DATABASE
        order_by = ('-joined_at',)

    @classmethod
    def create_user(cls, username, email, password, admin=False):
        try:
            with DATABASE.transaction():
                cls.create(
                    username=username,
                    email=email,
                    password=generate_password_hash(password),
                    is_admin=admin)
        except IntegrityError:
            raise ValueError("User already exists")


class Entry(Model):
    title = CharField()
    date = DateTimeField(default=datetime.datetime.now)
    time_spent = IntegerField()
    learned = TextField()
    resources = TextField()
    user = ForeignKeyField(
        rel_model=User,
        related_name='entries'
    )

    class Meta:
        database = DATABASE
        order_by = ('-date',)

    @classmethod
    def create_entry(cls, user, title, time_spent, learned, resources, date):
        try:
            with DATABASE.transaction():
                cls.create(
                    user=user,
                    title=title,
                    time_spent=time_spent,
                    date=date,
                    learned=learned,
                    resources=resources
                )
        except IntegrityError:
            raise ValueError("Entry already exists")


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Entry, Resource], safe=True)
    try:
        User.create_user(
            username='Gman',
            email='gman@gmail.com',
            password='password'
        )
    except ValueError:
        pass
    user = User.select().get()
    Entry.create_entry(
        title='Create Journal',
        date=datetime.datetime.strptime('2017-4-17', '%Y-%m-%d'),
        time_spent=3,
        learned='The innerworkings of a python web framework',
        resources='Flask docs - http://flask.pocoo.org/docs/0.12/',
        user=user
        )
    Entry.create_entry(
        title='Learn flask',
        date=datetime.datetime.strptime('2017-4-17', '%Y-%m-%d'),
        time_spent=3,
        learned='The innerworkings of a python web framework',
        resources='Flask docs - http://flask.pocoo.org/docs/0.12/',
        user=user
    )

    DATABASE.close()
