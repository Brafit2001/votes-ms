from http import HTTPStatus

from flask import jsonify


class EmptyDbException(Exception):
    """Exception raised when an API returns an empty.

        Attributes:
            message -- explanation of the error
            error_code -- code of the error
    """

    def __init__(self, message):
        super().__init__(message)
        self.message = message
        self.error_code = HTTPStatus.NO_CONTENT


class NotFoundException(Exception):
    """Exception raised when an API returns an empty.

        Attributes:
            message -- explanation of the error
            error_code -- code of the error
    """

    def __init__(self, message):
        super().__init__(message)
        self.message = message
        self.error_code = HTTPStatus.NOT_FOUND


class NotAuthorized(Exception):
    """Exception raised when user is not authorized to.

        Attributes:
            message -- explanation of the error
            error_code -- code of the error
    """

    def __init__(self, message):
        super().__init__(message)
        self.message = message
        self.error_code = HTTPStatus.UNAUTHORIZED


def handle_maria_db_exception(ex):
    message = str(ex)
    if 'foreign key constraint fails' in str(ex) and 'FOREIGN KEY (`reel`)' in str(ex):
        message = 'The reel does not exist'
    elif 'foreign key constraint fails' in str(ex) and 'FOREIGN KEY (`topic`)' in str(ex):
        message = 'The topic does not exist'
    return jsonify({'message': message, 'success': False})
