#!/usr/bin/python
# -*- coding: utf-8  -*-

'''
and you'll get a soup.page object that can be explored; its tree is more or less:
page
   block
      text
         par
            line
                charparams
                formatting
'''

from bs4 import BeautifulSoup
import lxml, gzip,pickle
from os import system,listdir,getcwd,path

import sys

from xml.etree import ElementTree


def load_to_bs(filename):
    f = open(filename,"r")
    text = f.read()
    bs = BeautifulSoup(text, "xml") #unicode(text, "utf-8"), "xml")
    f.close()
    return bs


def convert_xml_dsed(xml):
    dsed = "select; remove-ant; remove-txt\n"
    document = xml.find("document")
    pages = document.find_all("page")

    for page_n, page in enumerate(pages):
        page_w = page.attrs["width"]
        page_h = page.attrs["height"]
        dsed += "\nselect " + page_n + "\nset-txt\n(page 0 0 " + page_w + " " + page_h
        blocks = page.find_all("block")
        for block in blocks:
            texts = block.find_all("text")
            for text in texts:
                pars = text.find_all("par")
                for par in pars:
                    lines = par.find_all("line")
                    for line in lines:
                        dsed += "\n (line x y x y \"" 
                        chars = line.find_all("charParams")
                        for char in chars:
                            dsed += char.get_text()
                            dsed += "\")"
        dsed += "\n)\n\n."
    return dsed


def save(text, filename):
    f = open(filename, "w")
    f.write(text)
    f.close()


if __name__ == "__main__":
    xmlfile = sys.argv[1]
    xml = load_to_bs(xmlfile)
    dsed = convert_xml_dsed(xml)
    save(dsed, xmlfile + ".dsed")
