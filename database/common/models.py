from datetime import datetime

import peewee as pw

db = pw.SqliteDatabase('TG_BOT.db')


class ModelBase(pw.Model):
    created_at = pw.DateField(default=datetime.now())

    class Meta():
        database = db


class History(ModelBase):
    request_name = pw.TextField()
    message = pw.TextField()
