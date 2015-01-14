from test import TestDialog
from cal import CalendarDialog
from phrase import PhraseDialog
from server import ServerDialog


class ToolBar(object):
    """
    A class to design some buttons on tool bar
    """
    def __init__(self, parent):
        self.parent = parent

    def track_learning(self, e):
        """
        Event raises when learning tracking button is clicked
        """
        print 'Clicked button: %s' % (e.GetEventObject().GetLabel())
        CalendarDialog(self.parent, 'Learning Tracking')

    def test_vocabulary(self, e):
        """
        Event raises when test button is clicked
        """
        print 'Clicked button: %s' % (e.GetEventObject().GetLabel())
        TestDialog(self.parent, 'Test Vocabulary')

    def view_phrases(self, e):
        """
        Event raises when when view phrases button is clicked
        """
        print 'Clicked button: %s' % (e.GetEventObject().GetLabel())
        PhraseDialog(self.parent, 'Ordinary Phrases/Topics')

    def configure_server(self, e):
        """
        Event raises when server configuration button is clicked
        """
        print 'Clicked button: %s' % (e.GetEventObject().GetLabel())
        ServerDialog(self.parent, 'View Configuration Servers')