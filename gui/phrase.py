import wx
from ObjectListView import ObjectListView, ColumnDefn
from utils import DATE_FORMAT
from dictionary.database import PhraseDB


class PhraseDialog(wx.Dialog):
    """
    A class to manage the ordinary phrases
    """
    def __init__(self, parent, title):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title, size=(640, 480))
        self.dataOlv = ObjectListView(self, wx.ID_ANY, style=wx.LC_REPORT | wx.SUNKEN_BORDER | wx.LC_SINGLE_SEL)
        self.nb_phrase_status = wx.StaticText(self, -1, 'Phrase number: ', style=wx.ALIGN_LEFT)
        self.phrase_db = PhraseDB()
        self.phrase_dict = self.phrase_db.load()
        self.view_phrases = []
        self.get_phrases()
        self.set_columns()
        self.dialog_design()
        self.ShowModal()

    def dialog_design(self):
        """
        Design interface dialog
        :return:
        """
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        control_sizer = self.create_control_sizer()
        status_sizer = self.create_status_sizer()
        self.update_nb_phrase()
        main_sizer.Add(control_sizer, 0, wx.LEFT | wx.TOP, 10)
        main_sizer.Add(self.dataOlv, 1, wx.ALL | wx.EXPAND, 10)
        main_sizer.Add(status_sizer, 0, wx.BOTTOM, 10)
        self.SetSizer(main_sizer)

    def create_control_sizer(self):
        """
        Create button controls on dialog
        :return:
        """
        control_grid_sizer = wx.BoxSizer(wx.HORIZONTAL)
        add_btn = wx.BitmapButton(self, -1, wx.Bitmap('icon/add.ico'), style=wx.BORDER_NONE)
        add_btn.SetToolTip(wx.ToolTip('Add new phrase'))
        add_btn.Bind(wx.EVT_BUTTON, self.add_phrase)
        delete_btn = wx.BitmapButton(self, -1, wx.Bitmap('icon/delete.ico'), style=wx.BORDER_NONE)
        delete_btn.SetToolTip(wx.ToolTip('Delete a phrase'))
        delete_btn.Bind(wx.EVT_BUTTON, self.delete_phrase)
        control_grid_sizer.Add(add_btn, 0, wx.RIGHT, 8)
        control_grid_sizer.Add(delete_btn, 1)
        return control_grid_sizer

    def create_status_sizer(self):
        """
        Create phrase number label
        :return:
        """
        status_sizer = wx.BoxSizer(wx.HORIZONTAL)
        status_sizer.Add(self.nb_phrase_status, 0, wx.LEFT, 10)
        return status_sizer

    def update_nb_phrase(self):
        """
        Update the phrase number
        :return:
        """
        self.nb_phrase_status.SetLabel('Phrase number: %s' % len(self.view_phrases))

    def set_columns(self):
        """
        Column design for data overlay
        :return:
        """
        self.dataOlv.SetColumns([
            ColumnDefn('Date', 'left', 100, 'date'),
            ColumnDefn('Phrase', 'left', 250, 'phrase'),
            ColumnDefn('Meaning', 'left', 250, 'meaning'),
        ])
        self.dataOlv.SetObjects(self.view_phrases)

    def get_phrases(self):
        """
        Get phrases saved in database
        :return:
        """
        self.view_phrases = []
        for k, v in self.phrase_dict.items():
            tmp_obj = Phrase(k, v[0], v[1])
            self.view_phrases.append(tmp_obj)
        self.view_phrases.sort(key=lambda p: (p.date, p.phrase), reverse=True)

    def add_phrase(self, e):
        """
        Event raises when add button is clicked
        :param e:
        :return:
        """
        phrase_box = wx.TextEntryDialog(None, 'Please enter a phrase: ', 'Sim', '')
        if phrase_box.ShowModal() == wx.ID_OK:
            new_phrase = phrase_box.GetValue().lower()
        else:
            phrase_box.Destroy()
            return
        phrase_box.Destroy()
        meaning_box = wx.TextEntryDialog(None, 'Please enter the meaning: ', 'Sim', '')
        if meaning_box.ShowModal() == wx.ID_OK:
            meaning = meaning_box.GetValue().lower()
            if new_phrase != "" and meaning != "":
                now = wx.DateTime.Now()
                today = now.Format(DATE_FORMAT)
                self.phrase_dict[new_phrase] = [meaning, today]
                self.phrase_db.save(self.phrase_dict)
                self.get_phrases()
                self.dataOlv.SetObjects(self.view_phrases)
                self.update_nb_phrase()
        meaning_box.Destroy()

    def delete_phrase(self, e):
        """
        Event raises when delete button is clicked
        :param e:
        :return:
        """
        selected_obj = self.dataOlv.GetSelectedObject()
        if selected_obj is not None:
            yes_no_box = wx.MessageDialog(None, 'Are you sure you want to delete this phrase?', 'Sim',  wx.YES_NO)
            if yes_no_box.ShowModal() == wx.ID_YES:
                del self.phrase_dict[selected_obj.phrase]
                self.phrase_db.save(self.phrase_dict)
                self.view_phrases = [w for w in self.view_phrases if w.phrase != selected_obj.phrase]
                self.dataOlv.SetObjects(self.view_phrases)
                self.update_nb_phrase()
            yes_no_box.Destroy()


class Phrase(object):
    """
    A class for displaying phrase data
    """
    def __init__(self, p_phrase, p_meaning, p_date):
        self.date = p_date
        self.phrase = p_phrase
        self.meaning = p_meaning