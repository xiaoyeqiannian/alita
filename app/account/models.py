from inc import db
from sqlalchemy.dialects import mysql
from sqlalchemy.sql import func
from sqlalchemy import (Column, Integer, BigInteger, String, DateTime, Date, ForeignKey,
                        SmallInteger, Text, Float, TEXT)
from inc.cached import cached


# 用户表
class User(db.Model):
    __tablename__ = 'user'
    __table_args__ = {"useexisting":True, 'mysql_charset':'utf8', 'mysql_engine':'InnoDB'}

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    name = db.Column("name", String(32), comment="姓名")
    password = db.Column("password", String(128))
    avatar = db.Column("avatar", String(128), comment="头像")
    email = db.Column("email", String(64), comment="email")
    phone = db.Column("phone", String(11))
    role_id = Column("role_id", Integer, ForeignKey('role.id'))
    group_id = Column("group_id", Integer, ForeignKey('group.id'))
    updated_at = db.Column("updated_at", DateTime, default=func.now(), onupdate=func.now())
    created_at = db.Column("created_at", DateTime, default=func.now())
    state = db.Column("state", mysql.TINYINT(display_width=1), nullable=False, default=1, comment=u"0:无效,1:有效,2:已拉黑")

    def __repr__(self):
        return '<id: %s name %r>' % (self.id, self.name)

    @classmethod
    def get(cls, _id):
        return db.session.query(User).get({'id': _id})


# 组织
class Group(db.Model):
    __tablename__ = 'group'
    __table_args__ = {"useexisting":True, 'mysql_charset':'utf8', 'mysql_engine':'InnoDB'}

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    name = db.Column("name", String(32))
    kind = db.Column("kind", mysql.TINYINT(display_width=1), nullable=False, default=1, comment="1:个人,2:团体")
    updated_at = db.Column("updated_at", DateTime, default=func.now(), onupdate=func.now())
    created_at = db.Column("created_at", DateTime, default=func.now())
    state = db.Column("state", mysql.TINYINT(display_width=1), nullable=False, default=1, comment="0:无效,1:有效,2:已删除")

    users = db.relationship('User', backref='group')

    @classmethod
    def get(cls, _id):
        return db.session.query(Group).get({'id': _id})


# 角色
class Role(db.Model):
    __tablename__ = 'role'
    __table_args__ = {"useexisting":True, 'mysql_charset':'utf8', 'mysql_engine':'InnoDB'}

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    name = Column("name", String(45), nullable=False, default="", comment=u"")
    menu = Column("menu", Text, nullable=True, default="", comment=u"")
    group_id = Column("group_id", Integer)
    updated_at = db.Column("updated_at", DateTime, default=func.now(), onupdate=func.now())
    created_at = db.Column("created_at", DateTime, default=func.now())
    state = Column("state", mysql.TINYINT(display_width=1), nullable=False, default=1, comment="0:无效,1:有效,2:已删除")

    users = db.relationship('User', backref='role')

    @classmethod
    def get(cls, _id):
        return db.session.query(Role).get({'id': _id})