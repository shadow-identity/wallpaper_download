# -*- coding: utf-8 -*-
"""Download wallpapers from www.australiangeographic.com.au
Positional argument:
path -- pathname of destination wallpapers directory

Optional arguments:
-v, --verbose -- affects both log file and stdout

Output:
- Image files saves into path directory with addition information about site
  and author (if exist) in Exif.Image.Copyright field.
- Log to stdout
- Log file wp_download.log (more detailed than log in stdout)

"""
#TODO: add exceptions
#TODO: add thumbnail to exif?

import urllib
import urllib2
import lxml.html
import logging
import argparse
from os.path import abspath, exists
from os import mkdir


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
        self.prewiev_url = image[0][0].attrib['href']
        if not self.prewiev_url.startswith('http'):
            self.prewiev_url = site_prefix + self.prewiev_url
        #TODO: remove author if None
        #TODO: remove <cr>'s inside .name, get another name when None
        self.name = image[1].text.rstrip()
        if 'owl' in page.name:
            print 'len(image) ', len(image)
            print 'len(image)[1] ', len(image[1])
            print 'image[1].text', image[1].text
            print 'image[1].tail', image[1][0].tail
            print 'image[1][0]', image[1][0].text
            print 'image[1][1]', image[1][1].text
            print 'image[1][2]', image[1][2].text
            print 'image[1][3]', image[1][3].text
        #Author in last but one element
        if image[1][len(image[1]) - 2] is not None:
            self.author = image[1][len(image[1]) - 2].text
        else:
            self.author = 'Not present in gallery'

    def get_original_image_url(self):
        """Get information from prewiev page, save it in attributes."""
        prewiev_html = urllib.urlopen(self.prewiev_url).read()
        prewiev_doc = lxml.html.document_fromstring(prewiev_html)
        self.image_url = prewiev_doc.xpath(
                        '//*[@id="content"]/p/a')[0].attrib['href']
        # getting file extention of image from it's url
        self.extention = '.' + self.image_url.rpartition('.')[2]

    def save_image(self):
        """Get path to save, download file and save it to destination."""
        """try:"""

        #Calculate full filepath, download image, write it to disk
        self.filename = args.path + self.name + self.extention
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

url = 'http://www.australiangeographic.com.au/journal/wallpaper'
site_prefix = 'http://www.australiangeographic.com.au'
html = urllib.urlopen(url).read()
doc = lxml.html.document_fromstring(html)

#Parsing command line arguments
parser = argparse.ArgumentParser(description=
    'Download wallpapers from %(url)s'
    'BSD license. Source: https://bitbucket.org/ambush_k3/wp_download'
    % locals())
parser.add_argument('-v', '--verbose',
    help='increase output verbosity', action='store_true')
parser.add_argument('path', help='path to save wallpapers')
args = parser.parse_args()

#Is given path valid?
if not abspath(args.path):
    logging.error('Path must be absolute!')
if not (args.path.endswith('/') or args.path.endswith('\\')):
    from sys import platform as _platform
    if _platform.startswith("linux") or _platform == "darwin":
        args.path = args.path + '/'
    elif _platform == "win32" or "cygwin":
        args.path = args.path + '\\'

#Is given path exist?
if not exists(args.path):
    mkdir(args.path)

#Configuring logger
if __debug__ or args.verbose:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

page = Image()
for image in doc.xpath('//*[@id="content"]/table/tr/td/div'):
    page.get_data_from_gallery(image)
    # FIXME: revert to normal state
    print page.name
    if 'hkjkj' in page.name:
        page.get_original_image_url()
        page.save_image()
        page.edit_exif()
