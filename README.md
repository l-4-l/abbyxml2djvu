abby2dsed.py - Converts Abby FineReader XML* to Dsed-File, embeddabe to DJVU.
* for example, for Public Domain scans you can get Abby-xml for free from archive.org, or use Free-to-Try version of FineReader, or buy a FineReader.

Example of ABBY xml (in DOWNLOAD OPTIONS - ABBYY GZ): https://archive.org/details/maupassant_selected_by_tolstoi_transl_lazareva_1894_rus

Usage:
  abby2dsed.py filename.xml

It will produce filename.dsed in a same folder (inside it just unicode text with bracket-like structure, human-readable and editable).
All coordinates are starting from left-down corner of each page.

To embed dsed to DJVU, use
  djvused -u -s -f filename.dsed filename.djvu

(djvused is a part of DJVULibre package in Linux, there are Windows and MacOS/OSX versions somewhere).

xml2dsed.py - I have used it as an example, it was published in italian Wikisource, you'll find a link inside
