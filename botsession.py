# -*- coding: utf-8 -*-

from uuid import uuid4
from datetime import datetime, timedelta

from flask.sessions import SessionInterface, SessionMixin
from werkzeug.datastructures import CallbackDict
from pymongo import MongoClient
from flask import g


class BotSession(CallbackDict, SessionMixin):

    def __init__(self, initial=None, user_id=None):
        CallbackDict.__init__(self, initial)
        self.user_id = user_id
        self.modified = False

class BotSessionInterface(SessionInterface):

    def __init__(self, host='localhost', port=27017, db='', collection='sessions'):
        client = MongoClient(host, port)
        self.store = client[db][collection]
        print(self.store)

    def open_session(self, app, request):
        user_id = getattr(g, 'user_id', None)
        print(user_id)
        if user_id:
            stored_session = self.store.find_one({'user_id': user_id})
            if stored_session:
                if stored_session.get('expiration') > datetime.utcnow():
                    print("aaa")
                    return BotSession(initial = stored_session['data'],
                                        user_id = stored_session['user_id'])
        print("bbbb")
        return BotSession(user_id = user_id)

    def save_session(self, app, session, response):
        if self.get_expiration_time(app, session):
            expiration = self.get_expiration_time(app, session)
        else:
            expiration = datetime.utcnow() + timedelta(hours=1)
        res = self.store.update({'user_id': session.user_id},
                          {'user_id': session.user_id,
                           'data': session,
                           'expiration': expiration}, True)
        print(res)
