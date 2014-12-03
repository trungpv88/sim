__author__ = 'User'
from sgmllib import SGMLParser


class DefParser(SGMLParser):
    """
    A parser to get definition of a word in website:
    www.oxforddictionaries.com

    """
    def __init__(self, verbose=0):
        SGMLParser.__init__(self, verbose)
        self.data = ""
        self.buffer = None

    def handle_data(self, data):
        """
        Copy data from html parser
        :param data:
        :return:
        """
        if self.buffer is not None:
            self.buffer += data

    def start_span(self, att=None):
        """
        Get data inside the 'span' tag with attribute class='definition'.
        This tag contains the definition of word.
        :param att:
        :return:
        """
        span = [v for k, v in att if k == 'class' and v == 'definition']
        if span:
            self.buffer = ""

    def end_span(self):
        """
        Finish reading data at the end of 'span' tag
        :return:
        """
        if self.buffer is not None:
            self.data += self.buffer + '\n'
        self.buffer = None