__author__ = 'User'
import wx
import wx.lib.agw.thumbnailctrl as tc
from urllib import FancyURLopener
import urllib2
import simplejson
import time


class WordDisplay(wx.Dialog):
    def __init__(self, parent, title, content):
        super(WordDisplay, self).__init__(parent, wx.ID_ANY, 'Definition of ' + title)
        self.content = content
        self.title = title
        main_sizer = self.design_interface()
        self.SetSizer(main_sizer)

    def design_interface(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        word_title = self.create_title()
        description_image = self.create_description_image()
        definition_box = self.create_definition_box()
        main_sizer.Add(word_title, 0, wx.ALIGN_CENTER_HORIZONTAL, 1)
        main_sizer.Add(description_image, 0, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(definition_box, 1, wx.EXPAND | wx.ALL, 10)
        return main_sizer

    def create_title(self):
        word_title = wx.StaticText(self, wx.ID_ANY, self.title, style=wx.ALIGN_CENTER_HORIZONTAL)
        word_title.SetForegroundColour(wx.Colour(255, 0, 0))
        font = wx.Font(18, wx.ROMAN, wx.NORMAL, wx.BOLD)
        word_title.SetFont(font)
        return word_title

    def create_description_image(self):
        description_image_sizer = wx.GridSizer(1, 1)
        thumbnails = tc.ThumbnailCtrl(self, size=(10, 10), thumboutline=tc.THUMB_OUTLINE_NONE,
                                      imagehandler=tc.NativeImageHandler)
        # thumbnails.EnableScroll(False)
        thumbnails.ShowDir('image/')
        thumbnails.ShowFileNames(False)
        # thumbnails.SetToolTip(wx.ToolTip('View result detail'))
        # thumbnails.EnableToolTips(True)
        # thumbnails.ShowComboBox(True)
        thumbnails.Bind(tc.EVT_THUMBNAILS_DCLICK, self.test)
        # thumbnails.SetToolTip(wx.ToolTip('View result detail'))
        # btn = wx.Button(self, wx.ID_ANY, 'xxx')
        # image = wx.Bitmap('image/tornado.jpg')
        # image_show = wx.StaticBitmap(self, wx.ID_ANY, image, size=(20, 20))
        description_image_sizer.Add(thumbnails, 1, wx.EXPAND | wx.ALL, 10)
        # description_image_sizer.Add(btn)
        return description_image_sizer

    def test(self, e):
        image_search = ImageSearch(self, 'Search images from google', self.title)
        image_search.ShowModal()

    def create_definition_box(self):
        definition_box_sizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, 'Definition'), orient=wx.VERTICAL)
        content_sizer = wx.BoxSizer(wx.VERTICAL)
        content_text = wx.TextCtrl(self, wx.ID_ANY, self.content, style=wx.TE_MULTILINE | wx.TE_READONLY)
        content_sizer.Add(content_text, 1, wx.EXPAND | wx.ALL, 10)
        definition_box_sizer.Add(content_sizer, 1, wx.EXPAND | wx.ALL)
        return definition_box_sizer


class ImageSearch(wx.Dialog):
    def __init__(self, parent, title, word):
        super(ImageSearch, self).__init__(parent, wx.ID_ANY, title)
        self.word = word
        self.design_interface()

    def design_interface(self):
        grid_sizer = wx.BoxSizer(wx.VERTICAL)
        images_sizer = self.create_images_box()
        controls_sizer = self.create_controls_box()
        grid_sizer.Add(images_sizer, 1, wx.EXPAND | wx.ALL, 10)
        grid_sizer.Add(controls_sizer, 1, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(grid_sizer)

    def create_images_box(self):
        image_sizer = wx.BoxSizer(wx.VERTICAL)
        thumbnails = tc.ThumbnailCtrl(self, size=(10, 10), thumboutline=tc.THUMB_OUTLINE_NONE,
                                      imagehandler=tc.NativeImageHandler)
        thumbnails.ShowDir('image/')
        thumbnails.ShowFileNames(False)
        image_sizer.Add(thumbnails, 1, wx.EXPAND | wx.ALL, 10)
        return image_sizer

    def create_controls_box(self):
        controls_sizer = wx.GridSizer(1, 2)
        search_btn = wx.Button(self, wx.ID_ANY, 'Search')
        search_btn.Bind(wx.EVT_BUTTON, self.get_images)
        choose_btn = wx.Button(self, wx.ID_ANY, 'Chose')
        controls_sizer.Add(search_btn)
        controls_sizer.Add(choose_btn)
        return controls_sizer

    def get_images(self, e):
        count = 0
        for i in range(0, 1):
            url = ('https://ajax.googleapis.com/ajax/services/search/images?' + 'v=1.0&q='+ self.word +
                   '&start='+str(i*4)+'&userip=MyIP')
            request = urllib2.Request(url, None, {'Referer': 'testing'})
            response = urllib2.urlopen(request)

            results = simplejson.load(response)
            data = results['responseData']
            data_info = data['results']

            opener = FancyURLopener()
            for u in data_info:
                count += 1
                opener.retrieve(u['unescapedUrl'], 'image/' + str(count) + '.jpg')

            time.sleep(1)
        # self.design_interface()