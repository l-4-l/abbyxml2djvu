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

result tree should be like:

select 2 #page number
set-txt
(page xmin ymin xmax ymax
  (column xmin ymin xmax ymax
    (region xmin ymin xmax ymax
      (para xmin ymin xmax ymax
        (line xmin ymin xmax ymax
          (word xmin ymin xmax ymax
            (char xmin ymin xmax ymax "V")
          )
        )
      )
    )
  )
)

but in fact page-para-line is enough
'''

from bs4 import BeautifulSoup
import lxml, gzip, pickle, sys, time
from os import system,listdir,getcwd,path


out_par = 1

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
        page_w = int(page.attrs["width"])
        page_h = int(page.attrs["height"])
        dsed += "\nselect " + str(page_n+1) + "\nset-txt\n(page 0 0 " + str(page_w) + " " + str(page_h)
        #print(page_n)
        blocks = page.find_all("block")
        for block in blocks:
            texts = block.find_all("text")
            for text in texts:
                pars = text.find_all("par")
                for par in pars:
                    if out_par == 1:
                        para_t = page_h # init with max value
                        para_b = 0      # init with min value
                        para_l = page_w # init with max value
                        para_r = 0      # init with min value

                    lines_out = []
                    lines = par.find_all("line")
                    for line in lines:
                        line_t = int(line.attrs["t"])
                        line_b = int(line.attrs["b"])
                        line_l = int(line.attrs["l"])
                        line_r = int(line.attrs["r"])
                        line_out = unicode("(line "+ str(line_l).ljust(4)+ " "+ str(page_h-line_t).ljust(4)+ " "+ str(line_r).ljust(4)+ " "+ str(page_h-line_b).ljust(4)+ " \"")
                        chars = line.find_all("charParams")
                        for char in chars:
                            if char.get_text() == "\"":
                                line_out += u"\u201D"
                            else:
                                line_out += char.get_text()
                        line_out += "\")"
                        lines_out.append(line_out)

                        if out_par == 1:
                            para_t = min(para_t, int(line_t))
                            para_b = max(para_b, int(line_b))
                            para_l = min(para_l, int(line_l))
                            para_r = max(para_r, int(line_r))

                    if out_par == 1 and len(lines_out) > 1:
                        dsed += "\n (para " + str(para_l).ljust(4)+ " "+ str(page_h-para_t).ljust(4)+ " "+ str(para_r).ljust(4)+ " "+ str(page_h-para_b).ljust(4)
                        for line in lines_out:
                            dsed += "\n  " + line
                        dsed += "\n )"
                    else: # no paragraph for single line
                        for line in lines_out:
                            dsed += "\n " + line



        dsed += "\n)\n\n."
    return dsed


def save(text, filename):
    f = open(filename, "w")
    f.write(text.encode("utf-8"))
    f.close()


if __name__ == "__main__":
    xmlfile = sys.argv[1]

    time1 = time.time()
    xml = load_to_bs(xmlfile)
    print("Loaded in " + str(time.time() - time1))

    time1 = time.time()
    dsed = convert_xml_dsed(xml)
    print("Converted in " + str(time.time() - time1))

    save(dsed, xmlfile + ".dsed")

