class BadRequest(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        super().__init__(message)

        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        output = dict(self.payload or ())
        output['error'] = self.message
        return output


class NotFoundRequest(BadRequest):
    status_code = 404


class UnauthorizedRequest(BadRequest):
    status_code = 403
