from ObjectListView import ObjectListView, ColumnDefn
from word.word import Word
from word.word_view import WordDisplay, ImageDB
import os.path
import wx
import thread
from dictionary.database import DataBase, LogDB
from word.pronunciation import AUDIO_DIR, OGG_EXTENSION
from utils import DATE_FORMAT


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
        # get word data
        self.status_bar = status_bar
        self.is_running_thread = True
        self.dict_db = DataBase()
        self.saved_words = self.dict_db.load()
        self.view_words = []
        self.log_db = LogDB()
        self.log = self.log_db.load()
        # display words on overlay
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
        for k, v in self.saved_words.items():
            tmp_obj = WordView(k, self.normalize_view_def(v), self.log.get(k, ' ')[0])
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
        if new_word not in self.saved_words.keys() and new_word != "":
            # take definition from server using multi thread to increase speed
            thread.start_new_thread(self.thread_word_definition, (new_word, w))
        # get word pronunciation from server and update 'sound' icon on overlay
        w.get_pronunciation()
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
            self.saved_words[new_word] = saved_def
            self.dict_db.save(self.saved_words)
            # display definition on overlay
            self.view_words.append(WordView(new_word, view_def, today))
            self.view_words.sort(key=lambda word: (word.date, word.value), reverse=True)
            self.dataOlv.SetObjects(self.view_words)
            # save date to log file
            self.log[new_word] = []
            self.log[new_word].append(today)
            self.log_db.save(self.log)
            # display word number on status bar
            self.status_bar.update_word_nb(len(self.view_words))
        self.is_running_thread = False
        thread.exit()

    def set_columns(self):
        """
        Column design for data overlay
        :return:
        """
        def sound_getter(word):
            if os.path.exists(AUDIO_DIR + word.value + OGG_EXTENSION):
                return self.sound

        def image_getter(word):
            image_db = ImageDB()
            image_dict = image_db.load()
            if len(image_dict.get(word.value, [])) > 0:
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
        selected_obj = self.dataOlv.GetSelectedObjects()
        for obj in selected_obj:
            w = Word(obj.value)
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
            for line in self.saved_words[selected_obj.value]:
                word_def += line.decode('utf-8') + '\n'
            word_view = WordDisplay(self, selected_obj.value.upper(), word_def)
            word_view.ShowModal()

    def delete_word(self, e):
        selected_obj = self.dataOlv.GetSelectedObject()
        if selected_obj is not None:
            yes_no_box = wx.MessageDialog(None, 'Are you sure you want to delete this word?', 'Sim',  wx.YES_NO)
            if yes_no_box.ShowModal() == wx.ID_YES:
                del self.saved_words[selected_obj.value]
                self.dict_db.save(self.saved_words)
                # print selected_obj.id - 1
                # tmp = [w.id for w in self.view_words if w.value == selected_obj.value]
                # print tmp
                # del self.view_words[selected_obj.id - 1]
                self.view_words = [w for w in self.view_words if w.value != selected_obj.value]
                self.dataOlv.SetObjects(self.view_words)
                if selected_obj.value in self.log.keys():
                    del self.log[selected_obj.value]
                    self.log_db.save(self.log)
                if os.path.exists(AUDIO_DIR + selected_obj.value + OGG_EXTENSION):
                    os.remove(AUDIO_DIR + selected_obj.value + OGG_EXTENSION)
                # display word number on status bar
                self.status_bar.update_word_nb(len(self.view_words))
            yes_no_box.Destroy()

