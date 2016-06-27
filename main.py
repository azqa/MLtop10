import sys
from collections import Counter
import itertools
import jmlr
import jmlr_proc
import springer_ai
from general import get_keywords_of_single_abstract


# Avoids some strange unicode error...
# <http://stackoverflow.com/questions/21129020/how-to-fix-unicodedecodeerror-ascii-codec-cant-decode-byte>
reload(sys)
sys.setdefaultencoding('utf8')


def main():
    # TODO: better cleaning: get rid of \n, math, non-ASCII
    jmlr_keywords = [get_keywords_of_single_abstract(abs) for abs in jmlr.maybe_pickle_abstracts()]
    jmlr_proc_keywords = [get_keywords_of_single_abstract(abs) for abs in jmlr_proc.maybe_pickle_abstracts()]
    springer_ai_keywords = [get_keywords_of_single_abstract(abs) for abs in springer_ai.maybe_pickle_springer_ai_raw_abstracts()]

    print 'Number of JMLR abstracts: {0}'.format(len(jmlr_keywords))
    print 'Number of JMLR Proceedings abstracts: {0}'.format(len(jmlr_proc_keywords))
    print 'Number of Springer AI abstracts: {0}'.format(len(springer_ai_keywords))
    print 'Total = {0}'.format(len(jmlr_keywords) + len(jmlr_proc_keywords) + len(springer_ai_keywords))

    keywords = list(itertools.chain(*jmlr_keywords))
    keywords += list(itertools.chain(*jmlr_proc_keywords))
    keywords += list(itertools.chain(*springer_ai_keywords))
    all_keywords = Counter(keywords)
    for k in Counter(all_keywords).most_common(30):
        print k

if __name__ == '__main__':
    main()

