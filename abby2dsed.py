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
        dsed += "\nselect " + str(page_n+1) + "\nset-txt\n(page 0 0 " + str(page_w) + " " + str(page_h)
        blocks = page.find_all("block")
        for block in blocks:
            texts = block.find_all("text")
            for text in texts:
                pars = text.find_all("par")
                for par in pars:
                    lines = par.find_all("line")
                    for line in lines:
                        line_t = line.attrs["t"]
                        line_b = line.attrs["b"]
                        line_l = line.attrs["l"]
                        line_r = line.attrs["r"]
                        dsed += "\n (line "+ line_l.ljust(4)+ " "+ str(int(page_h)-int(line_t)).ljust(4)+ " "+ line_r.ljust(4)+ " "+ str(int(page_h)-int(line_b)).ljust(4)+ " \"" 
                        chars = line.find_all("charParams")
                        for char in chars:
                            dsed += char.get_text()
                        dsed += "\")"
        dsed += "\n)\n\n."
    return dsed


def save(text, filename):
    f = open(filename, "w")
    f.write(text.encode("utf-8"))
    f.close()


if __name__ == "__main__":
    xmlfile = sys.argv[1]
    xml = load_to_bs(xmlfile)
    dsed = convert_xml_dsed(xml)
    save(dsed, xmlfile + ".dsed")

