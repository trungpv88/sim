#----------------------------------------------------------------------------
# Change log:
# 2014/12/24  - Version 1.0
# 2015/01/16  - Version 1.1
#----------------------------------------------------------------------------
# Goal:
# - Handle html data fetched from the definition server

from sgmllib import SGMLParser


class DefParser(SGMLParser):
    """
    A parser to get definition of a word in website:
    www.oxforddictionaries.com

    """
    def __init__(self, verbose=0):
        SGMLParser.__init__(self, verbose)
        self.has_pronunciation = False
        self.div_nb = 0
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
        span = [v for k, v in att if k == 'class' and (v == 'definition' or v == 'linebreaks')]
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

    def start_div(self, att=None):
        """
        Get data inside the 'div' tag with attribute class='headpron'.
        This tag contains the definition of word.
        :param att:
        :return:
        """
        div = [v for k, v in att if k == 'class' and v == 'headpron']
        # get only one pronunciation (in some cases, there are many pronunciations)
        if div and not self.has_pronunciation:
            self.has_pronunciation = True
            self.buffer = ""

    def end_div(self):
        """
        Finish reading data at the end of 'div' tag
        :return:
        """
        if self.buffer is not None:
            self.div_nb += 1
            # <div class ="headpron"> contains another <div> tag
            if self.div_nb == 2:
                self.buffer = self.buffer.translate(None, ' \n')
                self.buffer = self.buffer.replace("Pronunciation:", '')
                self.data += self.buffer + '\n'
                self.buffer = None