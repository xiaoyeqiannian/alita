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

    id = Column(Integer, primary_key=True, autoincrement=True)
    bid = db.Column(BigInteger, nullable=False, comment="唯一id")
    username = db.Column(String(64), comment="登陆名")
    name = db.Column(String(32), comment="真实姓名")
    password = db.Column(String(128))
    email = db.Column(String(32), comment="email")
    phone = db.Column(String(11))
    role_id = Column(Integer, ForeignKey('role.id'))
    organization_id = Column(Integer, ForeignKey('organization.id'))
    update_time = db.Column(DateTime, default=func.now(), onupdate=func.now())
    create_time = db.Column(DateTime, default=func.now())
    state = db.Column(mysql.TINYINT(display_width=1), nullable=False, default=1, comment=u"0:无效,1:有效,2:已拉黑")

    def __repr__(self):
        return '<id: %s username %r>' % (self.id, self.username)

    @classmethod
    def get(cls, _id):
        return db.session.query(User).get({'id': _id})

    @classmethod
    def get_by_bid(cls, bid):
        return db.session.query(User).filter(User.bid == bid).first()

# 组织
class Organization(db.Model):
    __tablename__ = 'organization'
    __table_args__ = {"useexisting":True, 'mysql_charset':'utf8', 'mysql_engine':'InnoDB'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    bid = db.Column(BigInteger, nullable=False, comment="唯一id")
    name = db.Column(String(32))
    kind = db.Column(mysql.TINYINT(display_width=1), nullable=False, default=1, comment="1:个人,2:团体")
    update_time = db.Column(DateTime, default=func.now(), onupdate=func.now())
    create_time = db.Column(DateTime, default=func.now())
    state = db.Column(mysql.TINYINT(display_width=1), nullable=False, default=1, comment="0:无效,1:有效,2:已删除")

    users = db.relationship('User', backref='organization')

    @classmethod
    def get(cls, _id):
        return db.session.query(Organization).get({'id': _id})

    @classmethod
    def get_by_bid(cls, bid):
        return db.session.query(Organization).filter(Organization.bid == bid).first()

# 角色
class Role(db.Model):
    __tablename__ = 'role'
    __table_args__ = {"useexisting":True, 'mysql_charset':'utf8', 'mysql_engine':'InnoDB'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(45), nullable=False, default="", comment=u"")
    menu = Column(Text, nullable=True, default="", comment=u"")
    organization_id = Column(Integer)
    state = Column(mysql.TINYINT(display_width=1), nullable=False, default=1, comment="0:无效,1:有效,2:已删除")

    users = db.relationship('User', backref='role')

    @classmethod
    def get(cls, _id):
        return db.session.query(Role).get({'id': _id})