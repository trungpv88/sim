#----------------------------------------------------------------------------
# Change log:
# 2014/12/24  - Version 1.0
# 2015/01/16  - Version 1.1
#             - Add line breaks and pronunciation word to list view
#----------------------------------------------------------------------------
# Goal:
# - Display all learnt words on a list view
# - Add, delete and view a selected word


import os.path
import wx
import thread
import shutil
import unicodedata
from ObjectListView import ObjectListView, ColumnDefn
from word.word import Word
from word.word_view import WordDisplay
from dictionary.database import DataBase
from word.pronunciation import AUDIO_DIR, OGG_EXTENSION
from utils import DATE_FORMAT, convert_string_to_ogg
from sound import play_message_sound, play_opening_sound, play_buzz_sound


class WordView(object):
    """
    A class for displaying word data
    """
    def __init__(self, w_value, w_definition, w_date, w_line_breaks='', w_pronunciation=''):
        self.date = w_date
        self.value = w_value
        self.definition = w_definition
        self.line_breaks = w_line_breaks
        self.pronunciation = w_pronunciation


class MainPanel(wx.Panel):
    """
    A region to view short information of learned words
    """
    def __init__(self, parent, status_bar):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.remove_audio_files()
        # get word data
        self.status_bar = status_bar
        self.is_running_thread = True
        self.db = DataBase()
        self.dict_db = self.db.load()
        self.word_definition = {}
        self.word_date = {}
        self.get_definition()
        self.view_words = []
        self.dataOlv = ObjectListView(self, wx.ID_ANY, style=wx.LC_REPORT | wx.SUNKEN_BORDER | wx.LC_SINGLE_SEL)
        self.sound = self.dataOlv.AddNamedImages('user', wx.Bitmap('icon/sound.ico'))
        self.image = self.dataOlv.AddNamedImages('user', wx.Bitmap('icon/picture.ico'))
        self.set_columns()
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.dataOlv, 1, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(main_sizer)
        self.view_data()
        self.status_bar.update_word_nb(len(self.word_definition))

    def new_panel(self):
        """
        Refresh overlay when open new database
        :return:
        """
        self.db = DataBase()
        self.dict_db = self.db.load()
        self.word_definition = {}
        self.word_date = {}
        self.get_definition()
        self.view_words = []
        self.view_data()
        self.status_bar.update_word_nb(len(self.word_definition))

    @staticmethod
    def remove_audio_files():
        """
        Clean audio tempo files
        Remove the folder and all files inside before recreate new folder
        :return:
        """
        if os.path.exists(AUDIO_DIR):
            shutil.rmtree(AUDIO_DIR)
        os.makedirs(AUDIO_DIR)

    def get_definition(self):
        """
        Get word definition from dictionary extracted from database
        :return:
        """
        for w, v in self.dict_db[0].items():
            self.word_definition[w] = v.get('definition', '')
            self.word_date[w] = v.get('date', '')

    @staticmethod
    def normalize_view_def(word):
        """
        Take the first definition of word to display on overlay
        :param word: ['line breaks', 'pronunciation', 'definition']
        :return:
        """
        try:
            word_view = ' '.join(word[0].split()[1:7])  # get 7 first words in definition
            word_view = word_view.translate(None, '.,') + ' ...'  # remove punctuations
            return word_view.decode('utf-8')
        except:
            raise
            # return 'Error: cannot display the first definition of word.'

    def saved_to_view_words(self):
        """
        Convert from saved words (taken from database under dictionary type) to view words
        :param:dictionary
        :return:
        """
        for k, v in self.word_definition.items():
            if self.word_date[k] != '':
                view_def = self.normalize_view_def(v[2:])
                tmp_obj = WordView(k, view_def, self.word_date[k], v[0].decode('utf-8'), v[1].decode('utf-8'))
                self.view_words.append(tmp_obj)
            else:
                # delete error words
                del self.word_definition[k]
                del self.dict_db[0][k]
        self.view_words.sort(key=lambda w: (w.date, w.value), reverse=True)

    def view_data(self):
        """
        Display word definition on overlay
        :return:
        """
        self.saved_to_view_words()
        self.dataOlv.SetObjects(self.view_words)

    def add_new_data(self, new_word):
        """
        Add a record to data overlay
        Note: Process remains running
        :param new_word:
        :return:
        """
        self.is_running_thread = True
        current_word_number = len(self.word_definition)
        has_new_word = False
        w = Word(value=new_word)
        # check whether new word exists or is blank
        if new_word != "":
            if new_word not in self.word_definition.keys():
                self.dict_db[0][new_word] = {}
                # take definition from server using multi thread to increase speed
                thread.start_new_thread(self.thread_add_new_data, (new_word, w))
            else:
                # self.is_running_thread = False
                msg_box = wx.MessageDialog(None, 'This word exists!', 'Sim', style=wx.OK | wx.ICON_EXCLAMATION)
                msg_box.ShowModal()
                msg_box.Destroy()
                return
        # wait until add new data thread terminates
        while self.is_running_thread:
            # only update when a new word was added
            if len(self.word_definition) != current_word_number:
                has_new_word = True
                break
        if has_new_word:
            self.status_bar.update_word_nb(len(self.word_definition))
        else:
            dlg = wx.MessageDialog(None, 'Can not find this word!', 'Sim', style=wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()

    def thread_add_new_data(self, new_word, w):
        """
        Create a thread to process the fetching definition word
        :param new_word:
        :param w:
        :return:
        """
        if not self.is_running_thread:
            self.is_running_thread = False
            thread.exit()
            return
        word_def = ''
        while word_def == '':
            word_def = w.get_definition()
            if word_def != '':
                # save definition to database and get it to display on overlay
                now = wx.DateTime.Now()
                today = now.Format(DATE_FORMAT)
                saved_def = DataBase.normalize_saved_def(word_def)
                view_def = self.normalize_view_def(saved_def[2:])
                self.word_definition[new_word] = saved_def
                self.dict_db[0][new_word]['definition'] = saved_def
                self.dict_db[0][new_word]['date'] = today
                # get word pronunciation from server and update 'sound' icon on overlay
                audio_str = w.get_pronunciation()
                self.dict_db[0][new_word]['audio'] = audio_str
                self.db.save(self.dict_db)
                # display definition on overlay
                word_view = WordView(new_word, view_def, today, saved_def[0].decode('utf-8'),
                                     saved_def[1].decode('utf-8'))
                self.dataOlv.AddObject(word_view)
                self.dataOlv.SortBy(0, False)
                play_message_sound()
            else:
                break
        self.is_running_thread = False
        thread.exit()

    def set_columns(self):
        """
        Column design for data overlay
        :return:
        """
        def sound_getter(word):
            if len(self.dict_db[0][word.value].get('audio', [])) > 0:
                return self.sound

        def image_getter(word):
            if len(self.dict_db[0][word.value].get('image', [])) > 0:
                return self.image

        self.dataOlv.SetColumns([
            ColumnDefn('Date', 'left', 100, 'date'),
            ColumnDefn('Word', 'left', 100, 'value'),
            ColumnDefn('Line breaks', 'left', 100, 'line_breaks'),
            ColumnDefn('Pronunciation', 'left', 120, 'pronunciation'),
            ColumnDefn('Definition', 'left', 280, 'definition'),
            ColumnDefn('', 'center', 20, 'music', imageGetter=sound_getter),
            ColumnDefn('', 'center', 20, 'image', imageGetter=image_getter)
        ])

        self.dataOlv.SetObjects(self.view_words)

    def add_word(self, e):
        """
        Event raises when add word button is clicked
        :param e:
        :return:
        """
        name_box = wx.TextEntryDialog(None, 'Please enter a new word: ', 'Sim', '')
        if name_box.ShowModal() == wx.ID_OK:
            new_word = name_box.GetValue().lower()
            new_word = unicodedata.normalize('NFKD', unicode(new_word)).encode('ascii', 'ignore')
            self.add_new_data(new_word)
        name_box.Destroy()

    def play_pronunciation(self, e):
        """
        Event raises when play button is clicked
        :return:
        """
        selected_obj = self.dataOlv.GetSelectedObject()
        if selected_obj is not None:
            audio_str = self.dict_db[0][selected_obj.value].get('audio', '')
            path = unicode(AUDIO_DIR + selected_obj.value + OGG_EXTENSION)
            if not os.path.exists(path) and len(audio_str) > 0:
                convert_string_to_ogg(audio_str, path)
            w = Word(selected_obj.value)
            w.pronounce()

    def view_definition(self, e):
        """
        Event raises when view definition button is clicked
        :param e:
        :return:
        """
        selected_obj = self.dataOlv.GetSelectedObject()
        if selected_obj is not None:
            word_line_breaks = self.word_definition[selected_obj.value][0]
            word_pronunciation = self.word_definition[selected_obj.value][1]
            word_def = ""
            for line in self.word_definition[selected_obj.value][2:]:
                word_def += line.decode('utf-8') + '\n'
            play_opening_sound()
            # print word_def
            word_view = WordDisplay(self, selected_obj.value.upper(), word_line_breaks, word_pronunciation, word_def)
            word_view.ShowModal()

    def delete_word(self, e):
        """
        Event raises when delete word button is clicked
        :param e:
        :return:
        """
        selected_obj = self.dataOlv.GetSelectedObject()
        if selected_obj is not None:
            yes_no_box = wx.MessageDialog(None, 'Are you sure you want to delete this word?', 'Sim',  wx.YES_NO)
            if yes_no_box.ShowModal() == wx.ID_YES:
                del self.word_definition[selected_obj.value]
                del self.dict_db[0][selected_obj.value]
                self.db.save(self.dict_db)
                self.dataOlv.RemoveObject(selected_obj)
                self.dataOlv.SortBy(0, False)
                # display word number on status bar
                self.status_bar.update_word_nb(len(self.word_definition))
                play_buzz_sound()
            yes_no_box.Destroy()

    def update_db(self):
        """
        Reload dictionary after the database is updated
        :return:
        """
        self.dict_db = self.db.load()
