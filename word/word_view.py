import wx
import wx.lib.agw.thumbnailctrl as tc
from urllib import FancyURLopener
import urllib2
import simplejson
from random import shuffle, randint
import os.path
from dictionary.database import DataBase
from gui.utils import convert_image_to_string, convert_string_to_image
import shutil
import thread
GOOGLE_IMAGE_SERVER = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:'
IMAGE_PATH_FORMAT = '%s/%s.jpg'


class WordDisplay(wx.Dialog):
    """
    A class to display word information including definitions and description images
    """
    def __init__(self, parent, title, content):
        super(WordDisplay, self).__init__(parent, wx.ID_ANY, 'Definition of ' + title)
        self.parent = parent
        self.is_running = True
        self.word_images_directory = 'image'
        if not os.path.exists(self.word_images_directory):
            os.makedirs(self.word_images_directory)
        self.title = title.lower()
        self.db = DataBase()
        self.dict_db = self.db.load()
        self.word_image = {}
        self.get_image()
        self.images_saved = self.word_image.get(self.title, [])
        self.load_from_db_to_image()
        self.content = content
        self.thumbnails = tc.ThumbnailCtrl(self, -1, thumboutline=tc.THUMB_OUTLINE_FULL,
                                           imagehandler=tc.NativeImageHandler)
        main_sizer = self.design_interface()
        self.SetSizer(main_sizer)
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def get_image(self):
        """
        Get word description image from dictionary extracted from database
        :return:
        """
        for w, v in self.dict_db[0].items():
            self.word_image[w] = v.get('image', [])

    def load_from_db_to_image(self):
        """
        Load string from database to save to images
        :return:
        """
        image_count = 0
        for image_str in self.images_saved:
            image_count += 1
            image = convert_string_to_image(image_str)
            image_path = IMAGE_PATH_FORMAT % (self.word_images_directory, str(image_count))
            image.save(image_path)

    def design_interface(self):
        """
        Create interface including parts: title, description images, definitions
        :return:
        """
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        word_title = self.create_title()
        description_image = self.create_description_image()
        definition_box = self.create_definition_box()
        close_btn = wx.Button(self, -1, 'OK', size=(80, 25))
        close_btn.Bind(wx.EVT_BUTTON, self.on_close)
        main_sizer.Add(word_title, 0, wx.ALIGN_CENTER_HORIZONTAL, 1)
        main_sizer.Add(description_image, 0, wx.EXPAND, 1)
        main_sizer.Add(definition_box, 1, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(close_btn, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
        return main_sizer

    def create_title(self):
        """
        Create word title on top of dialog
        :return:
        """
        word_title = wx.StaticText(self, wx.ID_ANY, self.title.upper(), style=wx.ALIGN_CENTER_HORIZONTAL)
        word_title.SetForegroundColour(wx.Colour(255, 0, 0))
        font = wx.Font(18, wx.ROMAN, wx.NORMAL, wx.BOLD)
        word_title.SetFont(font)
        return word_title

    def create_description_image(self):
        """
        Create region to show description images
        :return:
        """
        description_image_sizer = wx.BoxSizer(wx.VERTICAL)
        self.thumbnails.ShowFileNames(False)
        self.show_image_thumbs()
        change_image_btn = wx.Button(self, -1, 'Get randomly word description images from Google')
        change_image_btn.Bind(wx.EVT_BUTTON, self.change_description_images)
        description_image_sizer.Add(self.thumbnails, 1, wx.EXPAND | wx.ALL, 10)
        description_image_sizer.Add(change_image_btn, 0, wx.ALIGN_CENTER_HORIZONTAL)
        return description_image_sizer

    def change_description_images(self, e):
        """
        Event raises when change image button is clicked
        :param e:
        :return:
        """
        self.images_saved = []
        # select images in 20 first result images from google search
        rnd_number = randint(0, 20)
        url = ('https://ajax.googleapis.com/ajax/services/search/images?' + 'v=1.0&q=' + self.title +
               '&start=' + str(rnd_number) + '&userip=MyIP')
        request = urllib2.Request(url)
        response = urllib2.urlopen(request)
        results = simplejson.load(response)
        data = results['responseData']
        data_info = data['results']
        opener = FancyURLopener()
        shuffle(data_info)
        self.is_running = True
        thread.start_new_thread(self.thread_image, (data_info, opener))

    def thread_image(self, data_info, opener):
        """
        A thread to handle the processing searching images from google
        :param data_info:
        :param opener:
        :return:
        """
        if not self.is_running:
            self.is_running = False
            thread.exit()
            return
        count = 0
        for u in data_info:
            count += 1
            try:
                if not os.path.exists(self.word_images_directory):
                    os.makedirs(self.word_images_directory)
                image_path = IMAGE_PATH_FORMAT % (self.word_images_directory, str(count))
                # key 'imageId' to get ID of image (Note: key 'unescapedUrl' for origin url of image)
                opener.retrieve(GOOGLE_IMAGE_SERVER + u['imageId'], image_path)
                self.images_saved.append(convert_image_to_string(image_path))
            except IOError:
                print 'Please wait some seconds before fetching another images.'
            if len(self.images_saved) == 3:
                self.show_image_thumbs()
                self.is_running = False
                thread.exit()
                return
        self.is_running = False
        thread.exit()

    def create_definition_box(self):
        """
        Create a box to display definitions
        :return:
        """
        definition_box_sizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, 'Definition'), orient=wx.VERTICAL)
        content_sizer = wx.BoxSizer(wx.VERTICAL)
        content_text = wx.TextCtrl(self, wx.ID_ANY, self.content, style=wx.TE_MULTILINE | wx.TE_READONLY)
        content_sizer.Add(content_text, 1, wx.EXPAND | wx.ALL, 10)
        definition_box_sizer.Add(content_sizer, 1, wx.EXPAND | wx.ALL)
        return definition_box_sizer

    def on_close(self, e):
        """
        Event raises when the dialog is closed
        :param e:
        :return:
        """
        self.dict_db[0][self.title]['image'] = self.images_saved
        self.db.save(self.dict_db)
        self.parent.update_db()
        self.parent.set_columns()  # update image icon in list view
        self.Destroy()

    def show_image_thumbs(self):
        """
        Display thumbnails of image from a directory
        Note: ThumbnailCtrl does not support the viewing image from paths
        :return:
        """
        if os.path.exists(self.word_images_directory):
            self.thumbnails.ShowDir(self.word_images_directory)
            shutil.rmtree(self.word_images_directory)