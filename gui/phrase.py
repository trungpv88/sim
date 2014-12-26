import wx
from word.word import Word
from ObjectListView import ObjectListView, ColumnDefn
from word.pronunciation import AUDIO_DIR, OGG_EXTENSION
from utils import *
from dictionary.database import DataBase


class Phrase(object):
    """
    A class for displaying phrase data
    """
    def __init__(self, p_phrase, p_meaning, p_date):
        self.date = p_date
        self.phrase = p_phrase
        self.meaning = p_meaning


class TopicDialog(wx.Dialog):
    """
    A dialog receiving topic content from user
    """
    def __init__(self, parent, title):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, 'Topic', size=(450, 300))
        self.content_text = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_MULTILINE, size=(400, 200))
        self.title = title
        self.parent = parent
        self.design_interface()

    def design_interface(self):
        """
        Design interface for dialog
        """
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        topic_title = wx.StaticText(self, wx.ID_ANY, self.title.upper(), style=wx.ALIGN_CENTER_HORIZONTAL)
        topic_title.SetForegroundColour(wx.Colour(255, 0, 0))
        font = wx.Font(18, wx.ROMAN, wx.NORMAL, wx.BOLD)
        topic_title.SetFont(font)

        close_btn = wx.Button(self, -1, 'OK', size=(80, 25))
        close_btn.Bind(wx.EVT_BUTTON, self.on_close)

        main_sizer.Add(topic_title, 0, wx.ALIGN_CENTER_HORIZONTAL, 1)
        main_sizer.Add(self.content_text, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(close_btn, 0, wx.ALIGN_CENTER | wx.BOTTOM, 5)
        self.SetSizer(main_sizer)

    def on_close(self, e):
        """
        Event raises when close button is clicked
        """
        now = wx.DateTime.Now()
        today = now.Format(DATE_FORMAT)
        content = self.content_text.GetValue()
        self.parent.phrase_dict[self.title] = [content, today]
        self.parent.dict_db[self.parent.db_index][self.parent.lang_index][self.title] = [content, today]
        self.Destroy()


class ContentDialog(TopicDialog):
    """
    A dialog to view and edit content of phrase and topic
    """
    def __init__(self, parent, title, content):
        super(ContentDialog, self).__init__(parent, title)
        self.content_text.SetValue(content)
        self.SetTitle('Content')

    def on_close(self, e):
        """
        Event raises when close button is clicked
        """
        confirm_msg_dlg = wx.MessageDialog(None, 'Are you sure you want to change this content?', 'Sim',
                                           style=wx.YES_NO | wx.ICON_EXCLAMATION)
        if confirm_msg_dlg.ShowModal() == wx.ID_YES:
            super(ContentDialog, self).on_close(e)
            self.parent.db.save(self.parent.dict_db)
            self.parent.get_phrases()
            self.parent.dataOlv.SetObjects(self.parent.view_phrases)
            self.parent.update_nb_phrase()
        else:
            self.Destroy()
        confirm_msg_dlg.Destroy()


class PhraseDialog(wx.Dialog):
    """
    A class to manage the ordinary phrases
    """
    def __init__(self, parent, title):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title, size=(640, 480))
        self.parent = parent
        self.dataOlv = ObjectListView(self, wx.ID_ANY, style=wx.LC_REPORT | wx.SUNKEN_BORDER | wx.LC_SINGLE_SEL)
        self.sound = self.dataOlv.AddNamedImages('user', wx.Bitmap('icon/sound.ico'))
        self.nb_status = wx.StaticText(self, -1, 'Total number: ', style=wx.ALIGN_RIGHT)
        self.db = DataBase()
        self.dict_db = self.db.load()
        self.db_index = 1
        self.lang_index = 0
        self.phrase_dict = self.dict_db[self.db_index][self.lang_index]
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
        add_btn.SetToolTip(wx.ToolTip('Add new phrase/topic'))
        add_btn.Bind(wx.EVT_BUTTON, self.add_phrase)
        delete_btn = wx.BitmapButton(self, -1, wx.Bitmap('icon/delete.ico'), style=wx.BORDER_NONE)
        delete_btn.SetToolTip(wx.ToolTip('Delete a phrase/topic'))
        delete_btn.Bind(wx.EVT_BUTTON, self.delete_phrase)
        add_audio_btn = wx.BitmapButton(self, -1, wx.Bitmap('icon/add_sound.ico'), style=wx.BORDER_NONE)
        add_audio_btn.SetToolTip(wx.ToolTip('Add audio file'))
        add_audio_btn.Bind(wx.EVT_BUTTON, self.add_audio_file)
        play_audio_btn = wx.BitmapButton(self, -1, wx.Bitmap('icon/play_pronunciation.ico'), style=wx.BORDER_NONE)
        play_audio_btn.SetToolTip(wx.ToolTip('Play audio file'))
        play_audio_btn.Bind(wx.EVT_BUTTON, self.play_audio_file)
        content_btn = wx.BitmapButton(self, -1, wx.Bitmap('icon/content.ico'), style=wx.BORDER_NONE)
        content_btn.SetToolTip(wx.ToolTip('View/Edit content'))
        content_btn.Bind(wx.EVT_BUTTON, self.view_edit_content)
        switch_lang_btn = wx.BitmapButton(self, -1, wx.Bitmap('icon/fr-eng.png'), style=wx.BORDER_NONE)
        switch_lang_btn.SetToolTip(wx.ToolTip('Change language'))
        switch_lang_btn.Bind(wx.EVT_BUTTON, self.change_language)
        switch_mode_btn = wx.BitmapButton(self, -1, wx.Bitmap('icon/switch.ico'), style=wx.BORDER_NONE)
        switch_mode_btn.SetToolTip(wx.ToolTip('Change phrase/topic'))
        switch_mode_btn.Bind(wx.EVT_BUTTON, self.change_mode)
        close_btn = wx.BitmapButton(self, -1, wx.Bitmap('icon/close.ico'), style=wx.BORDER_NONE)
        close_btn.SetToolTip(wx.ToolTip('Close'))
        close_btn.Bind(wx.EVT_BUTTON, self.on_close)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        control_grid_sizer.Add(add_btn, 0, wx.RIGHT, 8)
        control_grid_sizer.Add(delete_btn, 0, wx.RIGHT, 8)
        control_grid_sizer.Add(add_audio_btn, 0, wx.RIGHT, 8)
        control_grid_sizer.Add(play_audio_btn, 0, wx.RIGHT, 8)
        control_grid_sizer.Add(content_btn, 0, wx.RIGHT, 8)
        control_grid_sizer.Add(switch_lang_btn, 0, wx.RIGHT, 8)
        control_grid_sizer.Add(switch_mode_btn, 0, wx.RIGHT, 8)
        control_grid_sizer.Add(close_btn, 1)
        return control_grid_sizer

    def create_status_sizer(self):
        """
        Create phrase number label
        :return:
        """
        status_sizer = wx.BoxSizer(wx.HORIZONTAL)
        status_sizer.Add(self.nb_status, 1, wx.RIGHT, 10)
        return status_sizer

    def update_nb_phrase(self):
        """
        Update the phrase number
        :return:
        """
        if self.lang_index == 0:
            lang = 'eng'
        else:
            lang = 'fr'
        if self.db_index == 1:
            mode = 'phrase'
        else:
            mode = 'topic'
        self.nb_status.SetLabel('Total number: %s (%s-%s)' % (len(self.view_phrases), lang, mode))

    def set_columns(self):
        """
        Column design for data overlay
        :return:
        """
        def sound_getter(phrase):
            if len(self.dict_db[self.db_index][self.lang_index][phrase.phrase]) > 2:  # [meaning, today, audio]
                return self.sound

        self.dataOlv.SetColumns([
            ColumnDefn('Date', 'left', 100, 'date'),
            ColumnDefn('Phrase/Topic', 'left', 240, 'phrase'),
            ColumnDefn('Meaning/Content', 'left', 240, 'meaning'),
            ColumnDefn('', 'center', 20, 'music', imageGetter=sound_getter)
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

    @staticmethod
    def remove_char(unicode_str):
        translate_table = dict((ord(char), u'') for char in u'/')
        return unicode_str.translate(translate_table)

    def add_phrase(self, e):
        """
        Event raises when add button is clicked
        :param e:
        :return:
        """
        phrase_box = wx.TextEntryDialog(None, 'Please enter a phrase/topic: ', 'Sim')
        if phrase_box.ShowModal() == wx.ID_OK:
            new_item = phrase_box.GetValue().lower()  # remove forward slash (confuse with path)
            new_item = self.remove_char(new_item)
        else:
            phrase_box.Destroy()
            return
        phrase_box.Destroy()
        if self.db_index == 1:
            self.phrase_input_dlg(new_item)
        else:
            self.topic_input_dlg(new_item)
        self.db.save(self.dict_db)
        self.get_phrases()
        self.dataOlv.SetObjects(self.view_phrases)
        self.update_nb_phrase()

    def phrase_input_dlg(self, new_phrase):
        """
        Dialog receiving phrase meaning from user
        :param new_phrase:
        :return:
        """
        meaning_box = wx.TextEntryDialog(None, 'Please enter the meaning: ', 'Sim')
        if meaning_box.ShowModal() == wx.ID_OK:
            meaning = meaning_box.GetValue().lower()
            if new_phrase != "" and meaning != "":
                now = wx.DateTime.Now()
                today = now.Format(DATE_FORMAT)
                self.phrase_dict[new_phrase] = [meaning, today]
                self.dict_db[self.db_index][self.lang_index][new_phrase] = [meaning, today]
        meaning_box.Destroy()

    def topic_input_dlg(self, new_topic):
        """
        Dialog receiving topic content from user
        :param new_topic:
        :return:
        """
        topic_dlg = TopicDialog(self, new_topic)
        topic_dlg.ShowModal()

    def delete_phrase(self, e):
        """
        Event raises when delete button is clicked
        :param e:
        :return:
        """
        selected_obj = self.dataOlv.GetSelectedObject()
        if selected_obj is not None:
            yes_no_box = wx.MessageDialog(None, 'Are you sure you want to delete this phrase/topic?', 'Sim',  wx.YES_NO)
            if yes_no_box.ShowModal() == wx.ID_YES:
                del self.phrase_dict[selected_obj.phrase]
                # del self.dict_db[1][selected_obj.phrase]
                # not necessary because self.phrase_dict references to self.dict_db[1]
                self.db.save(self.dict_db)
                self.view_phrases = [w for w in self.view_phrases if w.phrase != selected_obj.phrase]
                self.dataOlv.SetObjects(self.view_phrases)
                self.update_nb_phrase()
            yes_no_box.Destroy()

    def update_overlay(self):
        """
        Update overlay content when change language/mode
        """
        self.phrase_dict = self.dict_db[self.db_index][self.lang_index]
        self.view_phrases = []
        self.get_phrases()
        self.dataOlv.SetObjects(self.view_phrases)
        self.update_nb_phrase()

    def change_language(self, e):
        """
        Event raises when change language button is clicked
        """
        choose_language = wx.SingleChoiceDialog(None, 'Choose your learning language:', 'Language',
                                                ['English', 'French'])
        if choose_language.ShowModal() == wx.ID_OK:
            lang = choose_language.GetStringSelection()
            if lang == 'English':
                lang_index = 0
            else:
                lang_index = 1
            if self.lang_index != lang_index:
                self.lang_index = lang_index
                self.update_overlay()
        choose_language.Destroy()

    def change_mode(self, e):
        """
        Event raises when change mode button is clicked
        """
        choose_mode = wx.SingleChoiceDialog(None, 'Choose your learning mode:', 'Mode',
                                            ['Phrase', 'Topic'])
        if choose_mode.ShowModal() == wx.ID_OK:
            mode = choose_mode.GetStringSelection()
            if mode == 'Phrase':
                mode_index = 1
            else:
                mode_index = 2
            if self.db_index != mode_index:
                self.db_index = mode_index
                self.update_overlay()
        choose_mode.Destroy()

    def view_edit_content(self, e):
        """
        Event raises when edit-view content button is clicked
        :param e:
        :return:
        """
        selected_obj = self.dataOlv.GetSelectedObject()
        if selected_obj is not None:
            content_dlg = ContentDialog(self, selected_obj.phrase, selected_obj.meaning)
            content_dlg.ShowModal()

    def add_audio_file(self, e):
        """
        Event raises when add audio button is clicked
        :param e:
        :return:
        """
        selected_obj = self.dataOlv.GetSelectedObject()
        if selected_obj is not None:
            open_dlg = wx.FileDialog(self.parent, 'Open audio file', '', '', 'mp3 files (*.mp3)|*.mp3',
                                     wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
            if open_dlg.ShowModal() == wx.ID_OK:
                audio_file_path = open_dlg.GetPath()
                ogg_file_path = AUDIO_DIR + selected_obj.phrase + OGG_EXTENSION
                convert_mp3_to_ogg(audio_file_path, ogg_file_path)
                audio_content = convert_ogg_to_string(ogg_file_path)
                self.dict_db[self.db_index][self.lang_index][selected_obj.phrase].append(audio_content)
                self.db.save(self.dict_db)
                self.dataOlv.SetObjects(self.view_phrases)
            open_dlg.Destroy()

    def play_audio_file(self, e):
        """
        Event raises when play audio file button is clicked
        :param e:
        :return:
        """
        selected_obj = self.dataOlv.GetSelectedObject()
        if selected_obj is not None:
            if len(self.dict_db[self.db_index][self.lang_index][selected_obj.phrase]) > 2:
                audio_str = self.dict_db[self.db_index][self.lang_index][selected_obj.phrase][2]
                path = AUDIO_DIR + selected_obj.phrase + OGG_EXTENSION
                if not os.path.exists(path) and len(audio_str) > 0:
                    convert_string_to_ogg(audio_str, path)
                p = Word(selected_obj.phrase)
                p.pronounce()

    def on_close(self, e):
        self.parent.panel.update_db()
        self.Destroy()