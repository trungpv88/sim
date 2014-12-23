import os.path
import wx
import thread
import shutil
from ObjectListView import ObjectListView, ColumnDefn
from word.word import Word
from word.word_view import WordDisplay
from dictionary.database import DataBase
from word.pronunciation import AUDIO_DIR, OGG_EXTENSION
from utils import DATE_FORMAT, convert_string_to_ogg


class WordView(object):
    """
    A class for displaying word data
    """
    def __init__(self, w_value, w_definition, w_date):
        self.date = w_date
        self.value = w_value
        self.definition = w_definition


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
        self.status_bar.update_word_nb(len(self.view_words))

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
        for w, v in self.dict_db.items():
            self.word_definition[w] = v['definition']
            self.word_date[w] = v['date']

    @staticmethod
    def normalize_view_def(word):
        """
        Take the first definition of word to display on overlay
        :param word:
        :return:
        """
        word_view = ' '.join(word[0].split()[1:15])  # get 15 first words in definition
        word_view = word_view.translate(None, '.,') + ' ...'  # remove punctuations
        return word_view

    def saved_to_view_words(self):
        """
        Convert from saved words (taken from database under dictionary type) to view words
        :param:dictionary
        :return:
        """
        for k, v in self.word_definition.items():
            tmp_obj = WordView(k, self.normalize_view_def(v), self.word_date[k])
            self.view_words.append(tmp_obj)
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
        w = Word(value=new_word)
        # check whether new word exists or is blank
        if new_word not in self.word_definition.keys() and new_word != "":
            self.dict_db[new_word] = {}
            # take definition from server using multi thread to increase speed
            thread.start_new_thread(self.thread_word_definition, (new_word, w))
        # get word pronunciation from server and update 'sound' icon on overlay
        if new_word != "":
            audio_str = w.get_pronunciation()
            self.dict_db[new_word]['audio'] = audio_str
        self.set_columns()  # update 'sound' icon for new word displayed on overlay

    def thread_word_definition(self, new_word, w):
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
        word_def = w.get_definition()
        if word_def is not '':
            # save definition to database and get it to display on overlay
            now = wx.DateTime.Now()
            today = now.Format(DATE_FORMAT)
            saved_def = DataBase.normalize_saved_def(word_def)
            view_def = self.normalize_view_def(saved_def)
            self.word_definition[new_word] = saved_def
            self.dict_db[new_word]['definition'] = saved_def
            self.dict_db[new_word]['date'] = today
            self.db.save(self.dict_db)
            # display definition on overlay
            self.view_words.append(WordView(new_word, view_def, today))
            self.view_words.sort(key=lambda word: (word.date, word.value), reverse=True)
            self.dataOlv.SetObjects(self.view_words)
            self.status_bar.update_word_nb(len(self.view_words))
        self.is_running_thread = False
        thread.exit()

    def set_columns(self):
        """
        Column design for data overlay
        :return:
        """
        def sound_getter(word):
            if len(self.dict_db[word.value].get('audio', [])) > 0:
                return self.sound

        def image_getter(word):
            if len(self.dict_db[word.value].get('image', [])) > 0:
                return self.image

        self.dataOlv.SetColumns([
            ColumnDefn('Date', 'left', 100, 'date'),
            ColumnDefn('Word', 'left', 100, 'value'),
            ColumnDefn('Definition', 'left', 500, 'definition'),
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
            self.add_new_data(new_word)
        name_box.Destroy()

    def play_pronunciation(self, e):
        """
        Event raises when play button is clicked
        :return:
        """
        selected_obj = self.dataOlv.GetSelectedObject()
        if selected_obj is not None:
            audio_str = self.dict_db[selected_obj.value].get('audio', '')
            path = AUDIO_DIR + selected_obj.value + OGG_EXTENSION
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
            word_def = ""
            for line in self.word_definition[selected_obj.value]:
                word_def += line.decode('utf-8') + '\n'
            word_view = WordDisplay(self, selected_obj.value.upper(), word_def)
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
                self.view_words = [w for w in self.view_words if w.value != selected_obj.value]
                self.dataOlv.SetObjects(self.view_words)
                del self.word_definition[selected_obj.value]
                del self.dict_db[selected_obj.value]
                self.db.save(self.dict_db)
                # display word number on status bar
                self.status_bar.update_word_nb(len(self.view_words))
            yes_no_box.Destroy()

    def update_db(self):
        """
        Reload dictionary after the database is updated
        :return:
        """
        self.dict_db = self.db.load()
