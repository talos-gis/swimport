from typing import Type, Union, Tuple


class AssertError:
    def __init__(self, exc_type: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception, text=None):
        self.exc_type = exc_type
        self.text = text
        self.exception = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not exc_type:
            assert False, 'expected an exception of type ' + str(self.exc_type) + ' to be thrown'
        self.exception = exc_val
        return issubclass(exc_type, self.exc_type) \
               and (self.text in (str(exc_val), None))
