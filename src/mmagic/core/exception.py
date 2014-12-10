
class MagicException(Exception):

    def __init__(self, message):
        self.message = message

    def message(self):
        return self.message

    def __str__(self):
        return message

    def get_message_list(self):
        return [self.message]

class MultiException(MagicException):

    def __init__(self):
        self.exceptions = []

    def __len__(self):
        return len(self.exceptions)

    def __str__(self):
        return str(self.get_message_list())

    def append(self, exception):
        self.exceptions.append(exception)

    def get_message_list(self):
        result = []
        for ex in self.exceptions:
            result += ex.get_message_list()
        return result

    def raise_if_not_empty(self):
        if len(self) > 0:
            raise self

class TooManyNotes(MagicException):

    def __init__(self, word):
        super(TooManyNotes, self).__init__('More than one note for "%s"'%word)
