from casbin import persist
from sqlalchemy import Column, Integer, String

import config
from inc import db

class CasbinRule(db.Model):
    __tablename__ = 'casbin_rule'
    __table_args__ = {"useexisting":True, 'mysql_charset':'utf8', 'mysql_engine':'InnoDB'}

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    ptype = Column(String(255))
    v0 = Column(String(255))
    v1 = Column(String(255))
    v2 = Column(String(255))
    v3 = Column(String(255))
    v4 = Column(String(255))
    v5 = Column(String(255))

    def __str__(self):
        arr = [self.ptype]
        for v in (self.v0, self.v1, self.v2, self.v3, self.v4, self.v5):
            if v is None:
                break
            arr.append(v)
        return ', '.join(arr)

    def __repr__(self):
        return '<CasbinRule {}: "{}">'.format(self.id, str(self))


class Adapter(persist.Adapter):
    """the interface for Casbin adapters."""

    def __init__(self, engine):
        self._engine = engine
        self._session = engine.session

    def load_policy(self, model):
        """loads all policy rules from the storage."""
        lines = self._session.query(CasbinRule).all()
        for line in lines:
            persist.load_policy_line(str(line), model)

    def _save_policy_line(self, ptype, rule):
        line = CasbinRule(ptype=ptype)
        for i, v in enumerate(rule):
            setattr(line, 'v{}'.format(i), v)
        self._session.add(line)

    def _commit(self):
        self._session.commit()

    def save_policy(self, model):
        """saves all policy rules to the storage."""
        query = self._session.query(CasbinRule)
        query.delete()
        for sec in ["p", "g"]:
            if sec not in model.model.keys():
                continue
            for ptype, ast in model.model[sec].items():
                for rule in ast.policy:
                    self._save_policy_line(ptype, rule)
        self._commit()
        return True

    def add_policy(self, sec, ptype, rule):
        """adds a policy rule to the storage."""
        self._save_policy_line(ptype, rule)
        self._commit()

    def remove_policy(self, sec, ptype, rule):
        """removes a policy rule from the storage."""
        query = self._session.query(CasbinRule)
        query = query.filter(CasbinRule.ptype == ptype)
        for i, v in enumerate(rule):
            query = query.filter(getattr(CasbinRule, 'v{}'.format(i)) == v)
        r = query.delete()
        self._commit()

        return True if r > 0 else False

    def remove_filtered_policy(self, sec, ptype, field_index, *field_values):
        """removes policy rules that match the filter from the storage.
        This is part of the Auto-Save feature.
        """
        query = self._session.query(CasbinRule)
        query = query.filter(CasbinRule.ptype == ptype)
        if not (0 <= field_index <= 5):
            return False
        if not (1 <= field_index + len(field_values) <= 6):
            return False
        for i, v in enumerate(field_values):
            query = query.filter(getattr(CasbinRule, 'v{}'.format(field_index + i)) == v)
        r = query.delete()
        self._commit()

        return True if r > 0 else False

    def __del__(self):
        self._session.close()

# 项目初始化，数据库还没有表时无法初始化adapter，需要在启动时，获取dp后再初始化
adapter = None
rbac = None