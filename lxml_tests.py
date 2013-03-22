# -*- coding: utf-8 -*-
"""Download wallpapers from www.australiangeographic.com.au"""
#TODO: add exceptions
#TODO: add thumbnail to exif?

import urllib
import urllib2
import lxml.html
import argparse


class Image():
    """Class containing attributes and methods assigned with image

    Attributes
    self.prewiev_url -- url of prewiev page
    self.image_url -- url of full image
    self.author -- author of image
    self.name -- full name of image (will be file name)
    self.extention -- file extention of image
    self.filename -- full name destination image file

    """

    def get_data_from_gallery(self, image):
        """Get useful information about image from gallery, save it in attrs

        Arguments:
        image -- ElementTree object containing values

        """
        #TODO: remove <cr>'s
        self.prewiev_url = image[0][0].attrib['href']
        if not self.prewiev_url.startswith('http'):
            self.prewiev_url = site_prefix + self.prewiev_url
        self.author = image[1][1].text
        #TODO: remove author if None
        self.name = image[1].text.rstrip()

    def get_original_image_url(self):
        """Get information from prewiev page, save it in attributes."""
        prewiev_html = urllib.urlopen(self.prewiev_url).read()
        prewiev_doc = lxml.html.document_fromstring(prewiev_html)
        self.image_url = prewiev_doc.xpath(
                        '//*[@id="content"]/p/a')[0].attrib['href']
        # getting file extention of image from it's url
        self.extention = '.' + self.image_url.rpartition('.')[2]

    def save_image(self):
        """Download file and save it to destination."""
        """try:"""
        self.filename = path_to_file + self.name + self.extention
        image_pointer = urllib2.urlopen(self.image_url)
        image = image_pointer.read()
        with open(self.filename, 'wb') as wallpaper_file:
            wallpaper_file.write(image)
        """except urllib2.URLError:
            logging.error('ERLError while saving img from %s', url)
        except IOError:
            logging.error('IOError while saving %s in %s', url, dest)
        else:"""
        image_pointer.close

    def edit_exif(self):
        """Manipulations with exif (adding copyright)."""
        import pyexiv2
        info_to_exif = ('File was downloaded from gallery {0}. \n'
                        'URL of image: {1} \n'
                        'Author: {2}'.format(
                                url, self.image_url, self.author))
        metadata = pyexiv2.ImageMetadata(self.filename)
        metadata.read()
        if 'Exif.Image.Copyright' in metadata:
            info_to_exif = metadata['Exif.Image.Copyright'].value + '\n' \
                           + info_to_exif
        metadata['Exif.Image.Copyright'] = info_to_exif
        metadata.write()

parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbose', help='increase output verbosity',
                    action='store_true')

url = 'http://www.australiangeographic.com.au/journal/wallpaper'
site_prefix = 'http://www.australiangeographic.com.au'
path_to_file = '/home/nedr/progs/wp_download/wp/'
html = urllib.urlopen(url).read()
doc = lxml.html.document_fromstring(html)
page = Image()
for image in doc.xpath('//*[@id="content"]/table/tr/td/div'):
    page.get_data_from_gallery(image)
    print page.name
    if 'Cormorant' in page.name:
        page.get_original_image_url()
        page.save_image()
        page.edit_exif()
