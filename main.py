import sys
from collections import Counter
import itertools
import jmlr
import jmlr_proc
import springer_ai
import IEEE_TPAMI
import IEEE_NN
from general import get_keywords_of_single_abstract


# Avoids some strange unicode error...
# <http://stackoverflow.com/questions/21129020/how-to-fix-unicodedecodeerror-ascii-codec-cant-decode-byte>
reload(sys)
sys.setdefaultencoding('utf8')


def main():
    # TODO: better cleaning: get rid of \n, math, non-ASCII
    source = dict()
    source['jmlr'] = [get_keywords_of_single_abstract(abs) for abs in jmlr.maybe_pickle_abstracts()]
    source['jmlr_proc'] = [get_keywords_of_single_abstract(abs) for abs in jmlr_proc.maybe_pickle_abstracts()]
    source['springer_ai'] = [get_keywords_of_single_abstract(abs) for abs in springer_ai.maybe_pickle_springer_ai_raw_abstracts()]
    source['IEEE_TPAMI'] = [get_keywords_of_single_abstract(abs) for abs in IEEE_TPAMI.maybe_pickle_abstracts()]
    source['IEEE_NN'] = [get_keywords_of_single_abstract(abs) for abs in IEEE_NN.maybe_pickle_abstracts()]

    print 'Number of JMLR abstracts: {0}'.format(len(source['jmlr']))
    print 'Number of JMLR Proceedings abstracts: {0}'.format(len(source['jmlr_proc']))
    print 'Number of Springer AI abstracts: {0}'.format(len(source['springer_ai']))
    print 'Number of IEEE TPAMI abstracts: {0}'.format(len(source['IEEE_TPAMI']))
    print 'Number of IEEE NN abstracts: {0}'.format(len(source['IEEE_NN']))
    print 'Total = {0}'.format(sum([len(s) for s in source.values()]))

    keywords = list(itertools.chain(*source['jmlr']))
    keywords += list(itertools.chain(*source['jmlr_proc']))
    keywords += list(itertools.chain(*source['springer_ai']))
    keywords += list(itertools.chain(*source['IEEE_TPAMI']))
    keywords += list(itertools.chain(*source['IEEE_NN']))
    all_keywords = Counter(keywords)
    for k in Counter(all_keywords).most_common(30):
        print k

if __name__ == '__main__':
    main()
