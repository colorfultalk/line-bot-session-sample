# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from flask.sessions import SessionInterface, SessionMixin
from werkzeug.datastructures import CallbackDict
from flask import g

from models import Session

class BotSession(CallbackDict, SessionMixin):

    def __init__(self, initial=None, user_id=None):
        CallbackDict.__init__(self, initial)
        self.user_id = user_id
        self.modified = False

class BotSessionInterface(SessionInterface):

    def open_session(self, app, request):
        user_id = getattr(g, 'user_id', None)
        print(user_id)
        if user_id:
            try:
                stored_session = Session.select().where(Session.user == user_id).get()
                if stored_session.expiration > datetime.utcnow():
                    return BotSession(initial=stored_session.data, user_id=stored_session.user)
                else:
                    return BotSession(user_id = user_id)
            except Session.DoesNotExist:
                return BotSession(user_id = user_id)
        # user_idがNoneの場合の処理を書く必要があるかも

    def save_session(self, app, session, response):
        expiration = datetime.utcnow() + timedelta(hours=1)
        try:
            stored_session = Session.select().where(Session.user == session.user_id).get()
            stored_session.data = session
            stored_session.expiration = expiration
            stored_session.save()
        except Session.DoesNotExist:
            Session.create(user=session.user_id, data=session, expiration=expiration)
