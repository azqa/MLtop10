# Algorithm will go through all subdirectories and work with all PDF files
import os
from os import walk

import time
from dill import dill
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter

from cStringIO import StringIO

PATH_TO_SPRINGER_ML_PDFS = "E:\\Workspaces\\MostPopularAlgorithmDatasets\\SpringerML\\NoProblemFiles"
PATH_TO_SPRINGER_ML_TXTS = "E:\\Workspaces\\MostPopularAlgorithmDatasets\\SpringerML\\ManuallyExtractedAbstracts"
#PATH_TO_SPRINGER_ML_PDFS = "E:\\Workspaces\\MostPopularAlgorithmDatasets\\SpringerML\\ExperimentsZone";

# PDFMiner reference:
# http://www.unixuser.org/~euske/python/pdfminer/programming.html


def all_paths_to_filetype(dirpath, extension):
    """ Iterates through all PDF files in a given directory and its subdirectories
    @param dirpath: path to iterate through
    """
    for (dirpath, dirnames, filenames) in walk(dirpath):
        for f in filenames:
            if f.endswith(extension):
                yield (dirpath+"\\"+f)

#TODO: all_abstracts_From_txts

def all_abstracts_from_txts(dirpath):
    """
    Iterates all abstracts from *.txt at the given path. Recursively goes through all subdirectories.
    @param dirpath: Root directory to start search for txts
    @return: list of abstracts + keywords
    """
    result_list = list()

    for filename in all_paths_to_filetype(dirpath,"txt"):
        print("Processing: "+filename)
        fp = open(filename, 'rb')
        abstract_list = list()
        for l in fp:
            abstract_list.append(l)
        abstract_str = ' '.join(abstract_list)
        result_list.append(abstract_str)
        print("Abstract + Keywords:")
        print(abstract_str)
        keyw = main.get_keywords_of_single_abstract(abstract_str) #Need to test that it does not crash
    return result_list

def all_abstracts_from_pdfs(dirpath):
    """
    Iterates all abstracts from PDFs at the given path. Recursively goes through all subdirectories.
    @param dirpath: Root directory to start search for PDF
    @return: list of abstracts + keywords
    """
    result_list = list()

    for filename in all_paths_to_filetype(dirpath,"pdf"):
        rsrcmgr = PDFResourceManager()
        laparams = LAParams()
        print("Processing: "+filename)
        fp = open(filename, 'rb')
        outfp = StringIO();
        device = TextConverter(rsrcmgr, outfp, codec='utf-8', laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        parser = PDFParser(fp)
        document = PDFDocument(parser)

        # Process first 2 pages in the document. Abstracts do not go further.
        pageIndex = 0
        for page in PDFPage.create_pages(document):
            interpreter.process_page(page)
            pageIndex += 1
            if pageIndex >= 2:
                break

        splitfiletxt = outfp.getvalue().split("\n")

        abstract_processed = False
        keywords_processed = False

        abstract_on = False
        waiting_for_keywords = False
        keywords_on = False

        abstract_list = list()
        keywords_list = list()

        abstract_lines = 1
        keyword_lines = 1

        for l in splitfiletxt:
            if l.startswith("Keywords") and abstract_on:
                abstract_on = False
                abstract_processed = True
                keywords_on = True
                keywords_list.append(l[8:])
            elif (l=="") and keywords_on:
                keywords_processed = True
                break
            elif abstract_on:
                abstract_list.append(l)
                abstract_lines += 1
            elif keywords_on:
                keywords_list.append(l)
            elif l == "Abstract":
                abstract_on = True
                # But don't append this time
            elif l.startswith("Abstract "):
                abstract_on = True
                abstract_list.append(l[9:])
            elif l.startswith("Abstract. "):
                abstract_on = True
                abstract_list.append(l[10:])

            if abstract_lines > 100:
                print("WARNING: very long abstract. Coding error?")
                abstract_processed = True
                break
            if keyword_lines > 5:
                print("WARNING: very long keywords list. Coding error?")
                keywords_processed = True
                break

        fp.close()
        abstract_str = ' '.join(abstract_list)
        keywords_str = ' '.join(keywords_list)
        final_str = abstract_str + keywords_str
        final_str = final_str.replace(u"\ufb01", 'fi')

        keyw = main.get_keywords_of_single_abstract(final_str)
        if not abstract_processed:
            print("Abstract not processed !!!")
        else:
            print("Abstract:")
            print(abstract_str)

        if not keywords_processed:
            print("!!!! Keywords not detected !!!!")
        else:
            print("Keywords: "+keywords_str)
        if len(keyw) == 0:
            print("BROKEN ABSTRACT !!!")
            print(final_str)
        #time.sleep(1)
        result_list.append(final_str)
    return result_list

SPRINGER_AI_FILE_RAW = 'springer_ai_proc_raw_abstracts'

def maybe_pickle_springer_ai_raw_abstracts(force=False):
    set_filename = '{0}.dill'.format(SPRINGER_AI_FILE_RAW)
    if os.path.exists(set_filename) and not force:
        print '{0} already present - Loading dill.'.format(set_filename)
        raw_abstracts = dill.load(open(set_filename, 'rb'))
    else:
        raw_abstracts = [i for i in all_abstracts_from_pdfs(PATH_TO_SPRINGER_ML_PDFS)]
        raw_abstracts.extend([i for i in all_abstracts_from_txts(PATH_TO_SPRINGER_ML_TXTS)])
        try:
            print 'Dilling {0}'.format(set_filename)
            dill.dump(raw_abstracts, open(set_filename, 'wb'))
        except Exception as e:
            print('Unable to save data to', set_filename, ':', e)
    return raw_abstracts

if __name__ == '__main__':
    import main

    index = 0
    for abstract in maybe_pickle_springer_ai_raw_abstracts():
        index+=1
        keyw = main.get_keywords_of_single_abstract(abstract)
        print(keyw)
        if (len(keyw)==0):
            print("ABSTRACT #"+str(index))
            print(abstract)