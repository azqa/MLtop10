# Avoids some strange unicode error...
# <http://stackoverflow.com/questions/21129020/how-to-fix-unicodedecodeerror-ascii-codec-cant-decode-byte>
import sys
import dill
import urllib2
from collections import defaultdict
from urlparse import urljoin
from bs4 import BeautifulSoup
import operator
from collections import Counter
import itertools

# git clone https://github.com/zelandiya/RAKE-tutorial
import rake

reload(sys)
sys.setdefaultencoding('utf8')


ROOT = 'http://www.jmlr.org/papers/'
VERSIONS = range(1, 17)
STOPPATH = 'SmartStoplist.txt'
RAKE_OBJECT = rake.Rake(STOPPATH)


def crawl_dump_raw_abstracts():
    res = defaultdict(lambda: defaultdict(set))

    total = 0
    for v in VERSIONS:
        volume_url = urljoin(ROOT, 'v{0}'.format(v))
        print 'Starting {0}'.format(volume_url)
        page = urllib2.urlopen(volume_url).read()
        soup = BeautifulSoup(page, 'html.parser')

        count = 0
        for link in soup.find_all('a'):
            # Only abstracts
            if 'abs' in link.text:
                publication = link['href']
                l_index = publication.rfind('/')
                r_index = publication.rfind('.html')
                publication = publication[l_index+1:r_index]

                # Do not take revisions
                if publication[-2] <> 'r':
                    print 'Reading {0}'.format(publication)

                    abstract_url = urljoin(volume_url, 'v{0}/{1}.html'.format(v, publication))
                    # print abstract_url
                    abstract_page = urllib2.urlopen(abstract_url).read()
                    abstract_soup = BeautifulSoup(abstract_page, 'html.parser')

                    res[v][publication] = abstract_soup.get_text()
                    count += 1
        print 'COUNT={0}'.format(count)
        total += count

    print 'TOTAL={0}'.format(total)
    dill.dump(res, file('jmlr_raw_abstracts.dill', 'w'))


def get_cut_abstracts(raw_abstracts):
    res = defaultdict(lambda: defaultdict(set))

    for v in VERSIONS:
        for k in raw_abstracts[v]:
            abstract = raw_abstracts[v][k]
            start_idx = abstract.find('Abstract')
            end_idx = abstract.rfind('abs')
            res[v][k] = abstract[start_idx + len('Abstract'):end_idx-1]

    return res

# TODO: better cleaning: get rid of \n, math etc


def get_keywords_of_single_abstract(abstract):
    sentence_list = rake.split_sentences(abstract)
    stopword_pattern = rake.build_stop_word_regex(STOPPATH)
    phrase_list = rake.generate_candidate_keywords(sentence_list, stopword_pattern)
    word_scores = rake.calculate_word_scores(phrase_list)
    keyword_candidates = rake.generate_candidate_keyword_scores(phrase_list, word_scores)
    sorted_keywords = sorted(keyword_candidates.iteritems(), key=operator.itemgetter(1), reverse=True)
    total_keywords = len(sorted_keywords)
    return [k[0] for k in sorted_keywords[0:total_keywords / 3]]


def get_keywords(abstracts):
    res = defaultdict(lambda: defaultdict(set))

    for v in VERSIONS:
        for k in abstracts[v]:
            res[v][k] = get_keywords_of_single_abstract(abstracts[v][k])

    return res


def main():
    raw_abstracts = dill.load(file('jmlr_raw_abstracts.dill'))
    cut_abstracts = get_cut_abstracts(raw_abstracts)
    # TODO: doesn't work yet
    keywords = get_keywords(cut_abstracts)
    keywords = [keywords[v, k] for v in VERSIONS for k in keywords[v]]
    keywords = list(itertools.chain(*keywords))
    all_keywords = Counter(keywords)
    print Counter(all_keywords).most_common(10)


if __name__ == '__main__':
    main()

