import traceback
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError, StatementError

import config
from .retcode import RETCODE

class ServerException(Exception):
    def __init__(self, message=None, data={}):
        self._message = message or self.__class__.message
        self._data = data
        super(Exception, self).__init__(self._message, self._data)

    @property
    def message(self):
        return self._message

    @property
    def data(self):
        return self._data

    def to_dict(self):
        code = self.__class__.code
        return {
            "code": code,
            "message": self._message,
            "data": self._data,
        }

    def __repr__(self):
        return str(self.to_dict())


class Success(ServerException):
    code = RETCODE.OK
    message = "success"


class ExceptionGroup(ServerException):
    code = -1
    message = "exception group"

    def __init__(self, e=None):
        message = str(e)
        data = {}
        if isinstance(e, Exception):
            data = {}
            message = "%s.%s: %s" % (
                e.__class__.__module__,
                e.__class__.__name__,
                e,
            )
            if config.DEBUG:
                data = {
                    "error": repr(e),
                    "traceback": traceback.format_exc(),
                }

        super(ExceptionGroup, self).__init__(message, data)


class UnknownException(ExceptionGroup):
    code = RETCODE.UNKOWNERR
    message = "system error!"


class UnderDevelopment(ServerException):
    code = RETCODE.UNDERDEBUG
    message = "under development"


class DatabaseException(ExceptionGroup):
    code = RETCODE.DBERR
    message = "db error!"

    def __init__(self, e=None):
        assert isinstance(SQLAlchemyError, e), type(e)

        if isinstance(e, StatementError):
            data = {}
            message = "%s.%s: [%s] %s" % (  # hide statement/params
                e.__class__.__module__,
                e.__class__.__name__,
                e.code,
                e.orig,
            )
            if config.DEBUG:
                data = {
                    "error": repr(e),
                    "traceback": traceback.format_exc(),
                }
            super(ExceptionGroup, self).__init__(message, data)

        else:
            super(DatabaseException, self).__init__(e)

class ThirdError(ServerException):
    code = RETCODE.THIRDERR
    message = "third error!"

class DataError(ServerException):
    code = RETCODE.DATAERR
    message = "data error!"

class IOError(ServerException):
    code = RETCODE.IOERR
    message = "io error!"

class LoginError(ServerException):
    code = RETCODE.PARAMERR
    message = "please sign in!"

class UserError(ServerException):
    code = RETCODE.USERERR
    message = "user error!"

class RoleError(ServerException):
    code = RETCODE.ROLEERR
    message = "role error!"

class PWDError(ServerException):
    code = RETCODE.PWDERR
    message = "password error!"

class VerifyError(ServerException):
    code = RETCODE.VERIFYERR
    message = "verify error!"

class ArgumentError(ServerException):
    code = RETCODE.LOGINERR
    message = "invalid argument!"

class ReqError(ServerException):
    code = RETCODE.REQERR
    message = "request error!"