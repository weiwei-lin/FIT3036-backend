class InvalidInput(Exception):
    def __init__(self, status_code=400, data=None):
        Exception.__init__(self)
        self.status_code = status_code
        self.data = data
