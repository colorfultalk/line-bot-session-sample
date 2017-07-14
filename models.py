from playhouse.postgres_ext import *
from datetime import datetime
import json

db = PostgresqlExtDatabase('bot', user='ippei-mu')

class BaseModel(Model):
    class Meta:
        database = db

class Session(BaseModel):
    id = PrimaryKeyField()
    user = CharField()
    data = BinaryJSONField()
    expiration = DateTimeField()

