__author__ = 'User'
import wx
import wx.lib.agw.thumbnailctrl as tc
from urllib import FancyURLopener
import urllib2
import simplejson
import time
from random import shuffle
import os.path
from dictionary.database import ImageDB
from gui.utils import convert_image_to_string, convert_string_to_image
import shutil
GOOGLE_IMAGE_SERVER = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:'


class WordDisplay(wx.Dialog):
    """
    A class to display word information including definitions and description images
    """
    def __init__(self, parent, title, content):
        super(WordDisplay, self).__init__(parent, wx.ID_ANY, 'Definition of ' + title)
        self.word_images_directory = 'image'
        self.title = title
        self.image_db = ImageDB()
        self.image_dict = self.image_db.load()
        self.images_saved = self.image_dict.get(self.title.lower(), [])
        self.load_from_db_to_image()
        self.content = content
        # self.word_images_directory = 'image/%s' % self.title.lower()
        if not os.path.exists(self.word_images_directory):
            os.makedirs(self.word_images_directory)
        self.thumbnails = tc.ThumbnailCtrl(self, -1, thumboutline=tc.THUMB_OUTLINE_FULL,
                                           imagehandler=tc.NativeImageHandler)
        main_sizer = self.design_interface()
        self.SetSizer(main_sizer)
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def load_from_db_to_image(self):
        image_count = 0
        for image_str in self.images_saved:
            image_count += 1
            image = convert_string_to_image(image_str)
            image_path = '%s/%s.jpg' % (self.word_images_directory, str(image_count))
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
        main_sizer.Add(word_title, 0, wx.ALIGN_CENTER_HORIZONTAL, 1)
        main_sizer.Add(description_image, 0, wx.EXPAND, 1)
        main_sizer.Add(definition_box, 1, wx.EXPAND | wx.ALL, 10)
        return main_sizer

    def create_title(self):
        """
        Create word title on top of dialog
        :return:
        """
        word_title = wx.StaticText(self, wx.ID_ANY, self.title, style=wx.ALIGN_CENTER_HORIZONTAL)
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
        self.thumbnails.ShowDir(self.word_images_directory)
        change_image_btn = wx.Button(self, -1, 'Get randomly word description images from Google Image Search')
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
        nb_images = 0
        self.images_saved = []
        # get first images from google search result
        rnd_numbers = [i for i in range(0, 10)]
        shuffle(rnd_numbers)
        for i in range(0, len(rnd_numbers)):
            # each request from encrypt server return a list of 4 images
            url = ('https://ajax.googleapis.com/ajax/services/search/images?' + 'v=1.0&q=' + self.title +
                   '&start=' + str(rnd_numbers[i] * 4) + '&userip=MyIP')
            request = urllib2.Request(url)
            response = urllib2.urlopen(request)

            results = simplejson.load(response)
            data = results['responseData']
            data_info = data['results']

            opener = FancyURLopener()
            shuffle(data_info)
            for u in data_info:
                nb_images += 1
                image_path = '%s/%s.jpg' % (self.word_images_directory, str(nb_images))
                # key 'imageId' to get ID of image (Note: key 'unescapedUrl' for origin url of image)
                opener.retrieve(GOOGLE_IMAGE_SERVER + u['imageId'], image_path)
                self.images_saved.append(convert_image_to_string(image_path))
                if nb_images == 3:
                    self.thumbnails.ShowDir(self.word_images_directory)
                    return
            # avoid to be blocked IP by google (this code can not be reached if data_info has more than 3 images)
            time.sleep(1)

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
        self.image_dict[self.title.lower()] = self.images_saved
        self.image_db.save(self.image_dict)
        shutil.rmtree(self.word_images_directory)
        os.makedirs(self.word_images_directory)
        self.Destroy()