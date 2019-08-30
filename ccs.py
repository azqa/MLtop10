import os
import main, time
import dill
import urllib2
from collections import defaultdict
from urlparse import urljoin
from bs4 import BeautifulSoup
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from cStringIO import StringIO

ROOT = 'https://dblp.uni-trier.de/'
YEARS = ('2010', '2011', '2012', '2013', '2014',
         '2018',
         '2015',
         '2016',
         '2017',
         '2019'
         )


def maybe_pickle_abstracts(force=False):
    file_name = 'ccs_abstracts'

    set_filename = '{0}.dill'.format(file_name)
    if os.path.exists(set_filename) and not force:
        print '{0} already present - Loading dill.'.format(set_filename)
        abstracts = dill.load(open(set_filename, 'rb'))
    else:
        abstracts = get_abstracts()
        abstracts = [abstracts[v][k] for v in YEARS for k in abstracts[v]]
        try:
            print 'Dilling {0}'.format(set_filename)
            dill.dump(abstracts, open(set_filename, 'wb'))
        except Exception as e:
            print('Unable to save data to', set_filename, ':', e)
    return abstracts


def get_abstracts():
    res = defaultdict(lambda: defaultdict(set))

    total = 0
    total_actual = 0
    for year in YEARS:
        year_url = urljoin(ROOT, 'search?q=conference%20on%20computer%20and%20communications%20security%20year%3A{0}%3A'.format(year))
        print 'Starting year {0}'.format(year)
        pub_req = urllib2.Request(year_url, headers={'User-Agent': "Magic Browser"})
        print(year_url)
        pub_page = urllib2.urlopen(pub_req).read()
        soup = BeautifulSoup(pub_page, 'html.parser')

        count = 0
        count_actual = 0
        heads = soup.findAll('div', {'class': 'head'})
        for head in heads:
            
            for link in head.find_all('a'):
                paper_url = link.get('href')

                #print(link)
                # Only abstracts
                if paper_url and 'https://doi.org/' in paper_url: # find the doi url
                    #try:
                    publication = paper_url
                    print 'Reading {0}'.format(paper_url)
                    
                    publication_url = urljoin('', paper_url)
                    paper_req = urllib2.Request(publication_url, headers={'User-Agent': "Magic Browser"})
                    paper_page = urllib2.urlopen(paper_req).read()
                    #print(paper_page)
                    abstract_soup = BeautifulSoup(paper_page, 'html.parser')
                    

                    link = abstract_soup.find('meta', {'name': 'citation_pdf_url'})
                    pdf_url = link.get('content')
                    #print("pdf url")
                    #print(pdf_url)
                    print 'PDF at {0}'.format(pdf_url)
                    paper_page = urllib2.urlopen(urllib2.Request(pdf_url , headers={'User-Agent': "Magic Browser"})).read()
                    fp = StringIO(paper_page)

                    rsrcmgr = PDFResourceManager()
                    laparams = LAParams()
                    outfp = StringIO();
                    device = TextConverter(rsrcmgr, outfp, codec='utf-8', laparams=laparams)
                    interpreter = PDFPageInterpreter(rsrcmgr, device)
                    for page in PDFPage.get_pages(fp, set(), maxpages=1, password="", caching=True, check_extractable=True):
                        interpreter.process_page(page)
                    time.sleep(1)
                    splitfiletxt = outfp.getvalue().split("\n")


                    abstract_processed = False
                    abstract_on = False

                    abstract_list = list()

                    abstract_lines = 1
                    prev = ''
                    for l in splitfiletxt:

                        if (l=='') and abstract_on and prev.lower() != 'abstract':
                            abstract_processed = True
                            break
                        elif abstract_on:
                            abstract_list.append(l)
                            abstract_lines += 1
                        elif l.lower() == "abstract":

                            abstract_on = True
                            # But don't append this time
                        elif l.lower().startswith("abstract "):
                            abstract_on = True
                            abstract_list.append(l[9:])
                        elif l.lower().startswith("abstract. "):
                            abstract_on = True
                            abstract_list.append(l[10:])

                        if abstract_lines > 100:
                            print("WARNING: very long abstract. Coding error?")
                            abstract_processed = True
                            break
                        prev = l

                        fp.close()
                        abstract_str = ' '.join(abstract_list)
                        final_str = abstract_str
                        final_str = final_str.replace(u"\ufb01", 'fi')
                        final_str = final_str.replace('- ', '')
                        

                    keyw = main.get_keywords_of_single_abstract_RAKE(final_str)
                    if not abstract_processed:
                        print("Abstract not processed !!!")
                        print(splitfiletxt)
                    else:
                        pass
                        #print("Abstract:")
                        #print(final_str)

                    if len(keyw) == 0:
                        print("BROKEN ABSTRACT !!!")
                        print(final_str)
                        print(splitfiletxt)
                    else:
                        res[year][publication] = final_str
                        count_actual += 1


                    #print(text)
                    #if 'Abstract Missing' not in text:

                        
                    count += 1

        print 'COUNT={0}/{1}'.format(count_actual, count)
        total += count
        total_actual += count_actual

    print 'TOTAL={0}/{1}'.format(total_actual, total)
    return res
