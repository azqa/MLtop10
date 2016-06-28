import sys
from collections import Counter
import itertools
import jmlr
import jmlr_proc
import springer_ai
import IEEE_general
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
    source['IEEE_TPAMI'] = [get_keywords_of_single_abstract(abs) for abs in IEEE_general.maybe_pickle_abstracts('IEEE_TPAMI')]
    source['IEEE_NN'] = [get_keywords_of_single_abstract(abs) for abs in IEEE_general.maybe_pickle_abstracts('IEEE_NN')]
    source['IEEE_NN_LS'] = [get_keywords_of_single_abstract(abs) for abs in IEEE_general.maybe_pickle_abstracts('IEEE_NN_LS')]

    total = 0
    for s in source.keys():
        count = len(source[s])
        total += count
        print 'Number of {0} abstracts: {0}'.format(s, count)

    print 'Total = {0}'.format(total)

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
