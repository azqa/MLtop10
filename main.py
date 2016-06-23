import sys
from collections import Counter
import itertools
from jmlr import maybe_pickle_abstracts as get_jmlr_abstracts
from jmlr_proc import maybe_pickle_abstracts as get_jmlr_proc_abstracts
from general import get_keywords_of_single_abstract


# Avoids some strange unicode error...
# <http://stackoverflow.com/questions/21129020/how-to-fix-unicodedecodeerror-ascii-codec-cant-decode-byte>
reload(sys)
sys.setdefaultencoding('utf8')


def main():
    # TODO: better cleaning: stemming, get rid of \n, math, non-ASCII
    jmlr_keywords = [get_keywords_of_single_abstract(abs) for abs in get_jmlr_abstracts()]
    jmlr_proc_keywords = [get_keywords_of_single_abstract(abs) for abs in get_jmlr_proc_abstracts()]

    keywords = list(itertools.chain(*jmlr_keywords))
    keywords += list(itertools.chain(*jmlr_proc_keywords))
    all_keywords = Counter(keywords)
    for k in Counter(all_keywords).most_common(30):
        print k

if __name__ == '__main__':
    main()

