import wx
import urllib2
GOOGLE_SERVER_IP = 'http://74.125.228.100'


class StatusBar(wx.StatusBar):
    """
    A class to design items on status bar
    """
    def __init__(self, parent):
        self.parent = parent
        self.status_bar = self.parent.CreateStatusBar()
        self.status_bar.SetFieldsCount(3)  # create 2 fields on status bar
        self.status_bar.SetStatusWidths([130, -1, 36])
        self.network_field = wx.BitmapButton(self.status_bar, -1, size=(16, 16), style=wx.BORDER_NONE)

        self.nb_word_status = wx.StaticText(self.status_bar, -1, 'Word number: ', style=wx.ALIGN_CENTER)
        self.reposition_field(self.nb_word_status, 0)

        self.update_network_status()
        self.network_field.SetToolTip(wx.ToolTip('Click to check internet connection'))
        self.network_field.Bind(wx.EVT_LEFT_DOWN, self.on_network_clicked)
        self.reposition_field(self.network_field, 2)

    def reposition_field(self, control, position):
        """
        Place item in one of fields of status bar
        :param control:item
        :param position:field
        :return:
        """
        field_rect = self.status_bar.GetFieldRect(position)
        control.SetRect(field_rect)

    def update_network_status(self):
        """
        Update network status image
        :return:
        """
        network_off = wx.Bitmap('icon/network_off.ico')
        network_on = wx.Bitmap('icon/network_on.ico')
        if self.is_connecting_internet():
            self.network_field.SetBitmapLabel(network_on)
        else:
            self.network_field.SetBitmapLabel(network_off)
        self.reposition_field(self.network_field, 1)

    @staticmethod
    def is_connecting_internet():
        """
        Check whether internet connection is available
        :return:
        """
        try:
            urllib2.urlopen(GOOGLE_SERVER_IP, timeout=2)  # host of google
            return True
        except urllib2.URLError as err:
            pass
        return False

    def on_network_clicked(self, e):
        """
        Event raises when network button is clicked
        :param e:
        :return:
        """
        self.update_network_status()

    def update_word_nb(self, nb):
        self.nb_word_status.SetLabel('Word number: %s' % nb)
