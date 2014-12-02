__author__ = 'User'
from sgmllib import SGMLParser


class DefParser(SGMLParser):
    def __init__(self, verbose=0):
        SGMLParser.__init__(self, verbose)
        self.data = ""
        self.buffer = None

    def handle_data(self, data):
        if self.buffer is not None:
            self.buffer += data

    def start_span(self, att=None):
        span = [v for k, v in att if k == 'class' and v == 'definition']
        if span:
            self.buffer = ""

    def end_span(self):
        if self.buffer is not None:
            self.data += self.buffer + '\n'
        self.buffer = None