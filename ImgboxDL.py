#!/usr/bin/python

import requests
import sys
import os
from html.parser import HTMLParser
import urllib.parse

url = sys.argv[1]

r = requests.get(url, allow_redirects=True)
img_links = []
img_dl_links = []

class GalleryParser(HTMLParser):
  handling_a = False
  last_link = ""

  def handle_starttag(self, tag, attrs):
    if (tag == "a"):
      if (attrs[0][0] == "href"):
        self.handling_a = True
        self.last_link = attrs[0][1]
    elif (tag == "img" and self.handling_a):
      img_links.append(self.last_link)

  def handle_endtag(self, tag):
    if (tag == "a" and self.handling_a):
      handling_a = False

print("Getting image links...")

gallery_parser = GalleryParser()
gallery_parser.feed(r.text)

print(str(len(img_links)) + " images found")

if (len(img_links) == 0):
  sys.exit("No images. Terminating script")

gallery = url.rsplit('/', 1)[-1]

print("Creating gallery folder " + gallery)

if (os.path.exists(gallery) and os.path.isdir(gallery)):
  print("Gallery folder exists... deleting")
  os.rmdir(gallery)

os.mkdir(gallery)
os.chdir(gallery)

print("Getting image download links")

class ImageParser(HTMLParser):
  handling_a = False
  last_link = ""

  def handle_starttag(self, tag, attrs):
    if (tag == "a"):
      if (attrs[0][0] == "href"):
        self.handling_a = True
        self.last_link = attrs[0][1]
    elif (tag == "i" and self.handling_a):
      if (attrs[0][0] == "class" and attrs[0][1] == "icon-cloud-download"):
        img_dl_links.append(self.last_link)

  def handle_endtag(self, tag):
    if (tag == "a" and self.handling_a):
      handling_a = False

for link in img_links:
  imgurl = "https://imgbox.com" + link
  print("Getting image download link for " + imgurl)

  r = requests.get(imgurl, allow_redirects=True)

  image_parser = ImageParser()
  image_parser.feed(r.text)

for img in img_dl_links:
  print("Getting " + img)
  
  r = requests.get(img, allow_redirects=True)

  url_parts = urllib.parse.urlparse(img)
  path_parts = url_parts[2].rpartition('/')
  imgpath = path_parts[2]

  print ("Saving to " + imgpath)

  file = open(imgpath, "wb")
  file.write(r.content)
  file.close()
