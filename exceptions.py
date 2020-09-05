"""
Internal logic exceptions. Contain a verbose message an a exception HTTP code. Any internal logic
process can raise a LogicException.
"""
from django.utils.translation import ugettext_lazy as _


class LogicException(Exception):

    def __init__(self, msg, http_code=400):
        self.__msg = msg
        self.__HTTP_code = http_code

    def getMsg(self):
        return self.__msg

    def getHTTP_code(self):
        return self.__HTTP_code

    def __str__(self):
        return self.__msg

    def details(self, msg):
        """
        Returns a copy of LogicException but with additions to error message.
        :param msg: <str>
        :return: <LogicException>
        """
        if isinstance(msg, Exception):
            msg = str(msg)
        self.__msg = self.__msg + ": " + msg
        return self


class NullAttributeException(LogicException):
    def __init__(self):
        super(NullAttributeException, self).__init__(
            _('The parameter passed to the function can not be null'), 400)


class IncorrectParametersException(LogicException):
    def __init__(self):
        super(IncorrectParametersException, self).__init__(_(
            'Some of the request parameters have generated an error'), 409)


class ResourceNotFoundException(LogicException):
    def __init__(self):
        super(ResourceNotFoundException, self).__init__(
            _('The requested resource does not exist'), 404)