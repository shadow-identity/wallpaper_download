# -*- coding: utf-8 -*-


import urllib
import urllib2
import lxml.html

url = 'http://www.australiangeographic.com.au/journal/wallpaper'
html_file = '/home/nedr/progs/wp_download/gallery.html'
site_prefix = 'http://www.australiangeographic.com.au'
path_to_file = '/home/nedr/progs/wp_download/wp/'
doc_file = open(html_file)
doc = lxml.html.document_fromstring(doc_file.read())
html = urllib.urlopen(url).read()
doc = lxml.html.document_fromstring(html)


class Image():
    def get_data_from_gallery(self, image):
        #TODO: remove <cr>'s
        self.prewiev_url = image[0][0].attrib['href']
        if not self.prewiev_url.startswith('http'):
            self.prewiev_url = site_prefix + self.prewiev_url
        self.author = image[1][1].text
        #TODO: remove author if None
        self.name = image[1].text

    def get_original_image_url(self):
        prewiev_html = urllib.urlopen(self.prewiev_url).read()
        prewiev_doc = lxml.html.document_fromstring(prewiev_html)
        self.image_url = prewiev_doc.xpath(
                        '//*[@id="content"]/p/a')[0].attrib['href']
        print self.image_url

    def save_image(self):
        """Download file from url and save it as dest."""
        """try:"""
        image_pointer = urllib2.urlopen(self.image_url)
        image = image_pointer.read()
        with open(path_to_file + self.name + '.jpg', 'wb') as wallpaper_file:
            wallpaper_file.write(image)
        """except urllib2.URLError:
            logging.error('ERLError while saving img from %s', url)
        except IOError:
            logging.error('IOError while saving %s in %s', url, dest)
        else:"""
        image_pointer.close

    def edit_exit(self):
        #TODO: write exif support
        """ pyexiv2
            see http://stackoverflow.com/questions/ \
            765396/exif-manipulation-library-for-python
            0x013b    315    Image    Exif.Image.Artist
            0x8298    33432    Image    Exif.Image.Copyright
        """

page = Image()
#TODO: add exceptions
for image in doc.xpath('//*[@id="content"]/table/tr/td/div'):
    page.get_data_from_gallery(image)
    page.get_original_image_url()
    page.save_image()
