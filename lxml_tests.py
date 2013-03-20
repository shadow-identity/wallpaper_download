# -*- coding: utf-8 -*-


import urllib
import lxml.html

url = 'http://www.australiangeographic.com.au/journal/wallpaper'
html_file = '/home/nedr/progs/wp_download/gallery.html'
site_prefix = 'http://www.australiangeographic.com.au'
doc_file = open(html_file)
doc = lxml.html.document_fromstring(doc_file.read())
#html = urllib.urlopen(url).read()
#doc = lxml.html.document_fromstring(html)


class Image():
    def get_data_from_gallery(self, image):
        self.prewiev_url = image.attrib["href"]
        if not self.prewiev_url.startswith('http'):
            self.prewiev_url = site_prefix + self.prewiev_url


page = Image()

for image in doc.xpath('//*[@id="content"]/table/tr/td/div/p/a'):
    page.get_prewiev_url(image)

"""doc.xpath('//*[@id="content"]/table/tr/td/div')[0][1][1].text
'David Bristow'

doc.xpath('//*[@id="content"]/table/tr/td/div')[0][1].text
'Green sea turtle, WA'

doc.xpath('//*[@id="content"]/table/tr/td/div')[0][0][0].attrib['href']
'http://www.australiangeographic.com.au/journal/images-of-australia-green-sea-turtle.htm'
"""
    #page.prewiev_url = image.attrib["href"]

#first_string = xml.xpath('.//*[@id="content"]/table/')
#              '//*[@id="content"]/table/tbody/tr[1]/td[1]/div/p[2]/em/text()')

#txt1 = xmldata.xpath('/html/body/span[@class="simple_text"]/text()[1]')
# Находим тег «span», у которого аттрибут «class» равен значению «simple_text»
# и с помощью функции text() получаем текст элемента
#txt2 = xmldata.xpath(
#     '/html/body/span[@class="cyrillic_text"]/following-sibling::text()[1]')
# Находим тег «span», у которого аттрибут «class» равен значению
# «cyrillic_text» и получаем следующий за ним текст с помощью following-sibling
# (получаем следующий в ветке элемент) и text()
# Для получение значений использовался XPath
