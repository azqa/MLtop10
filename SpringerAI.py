# Algorithm will go through all subdirectories and work with all PDF files
from os import walk

import sys
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter

from cStringIO import StringIO

PATH_TO_SPRINGER_ML_PDFS = "E:\\Workspaces\\MostPopularAlgorithmDatasets\\SpringerML";

# http://www.unixuser.org/~euske/python/pdfminer/programming.html

def all_paths_to_pdfs(dirpath):
    """ Iterates through all PDF files in a given directory and its subdirectories
    @param dirpath: path to iterate through
    """
    for (dirpath, dirnames, filenames) in walk(dirpath):
        for f in filenames:
            if f.endswith('pdf'):
                yield (dirpath+"\\"+f)

def all_abstracts_from_pdfs(dirpath):
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()

    for filename in all_paths_to_pdfs(dirpath):
        print filename
        fp = open(filename, 'rb')
        outfp = StringIO();
        device = TextConverter(rsrcmgr, outfp, codec='utf-8', laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        parser = PDFParser(fp)
        document = PDFDocument(parser)
        # Process each page contained in the document.
        for page in PDFPage.create_pages(document):
            interpreter.process_page(page)
        splitfiletxt = outfp.getvalue().split("\n");
        abstractOn = False
        abstractList = list()
        for l in splitfiletxt:
            if (l == ""):
                abstractOn = False
            if (abstractOn):
                abstractList.append(l)
            if (l=="Abstract"):
                abstractOn = True
        fp.close();
        abstractStr = ' '.join(abstractList)
        print(abstractStr)
        break #Only for tests

if __name__ == '__main__':
    all_abstracts_from_pdfs(PATH_TO_SPRINGER_ML_PDFS)