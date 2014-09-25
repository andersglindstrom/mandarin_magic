
class MagicException(Exception):

    def __init__(self, message):
        self.message = message

    def message(self):
        return self.message

    def get_message_list(self):
        return [self.message]

class MultiException(Exception):

    def __init__(self):
        self.exceptions = []

    def append(self, exception):
        self.exceptions.append(exception)

    def get_message_list(self):
        result = []
        for ex in self.exceptions:
            result += ex.get_message_list()
        return result
