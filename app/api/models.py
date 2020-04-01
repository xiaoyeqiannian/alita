# coding: utf-8

from inc import db
from sqlalchemy.dialects import mysql
from sqlalchemy.sql import func
from sqlalchemy import (Column, Integer, String, DateTime, Date,
                        SmallInteger, Text, Float, TEXT)

class Account(db.Model):
    __tablename__ = "account"
    __table_args__ = {"useexisting": True, "mysql_charset": "utf8mb4", "mysql_engine": "InnoDB"}

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    phone = Column("phone", String(16), nullable=False, default="", doc=u"")
    nickname = Column("nickname", String(64), nullable=True, default="", doc=u"")
    password = Column("password", String(128), nullable=True, default="", doc=u"")
    update_time = Column("update_time", DateTime(timezone=True), default=func.now(), onupdate=func.now())
    create_time = Column("create_time", DateTime(timezone=True), default=func.now())
    state = Column("state", mysql.TINYINT(display_width=1), nullable=False, default="1", doc=u"")

    def __repr__(self):
        return "<Account %s,%s,%s>" % (self.id, self.nickname, self.phone)
