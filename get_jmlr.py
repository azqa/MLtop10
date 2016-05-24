# Avoids some strange unicode error...
# <http://stackoverflow.com/questions/21129020/how-to-fix-unicodedecodeerror-ascii-codec-cant-decode-byte>
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import urllib2
from collections import defaultdict
from urlparse import urljoin
from bs4 import BeautifulSoup
from nltk import word_tokenize
from nltk.corpus import stopwords


ROOT = 'http://www.jmlr.org/papers/'
VERSIONS = range(1, 17)
STOPWORDS = stopwords.words('english')


def main():
    res = defaultdict(lambda: defaultdict(set))

    for v in VERSIONS:
        volume_url = urljoin(ROOT, 'v{0}'.format(v))
        print 'Starting {0}'.format(volume_url)
        page = urllib2.urlopen(volume_url).read()
        soup = BeautifulSoup(page, 'html.parser')

        for link in soup.find_all('a'):
            # Only abstracts
            if link.text == 'abs':
                publication = link['href']
                abstract_url = urljoin(volume_url, publication)
                abstract_page = urllib2.urlopen(abstract_url).read()
                abstract_soup = BeautifulSoup(abstract_page, 'html.parser')

                # Multiple paragraphs possible
                all_p = abstract_soup.find_all('p')
                end_index = 0
                for idx, p in enumerate(all_p):
                    # End found
                    if '[abs]' in p or 'Home' in p.text or 'div' in p.text:
                        end_index = idx
                        break
                if end_index == 0:
                    print 'Error for {0}'.format(abstract_url)

                # Element 0 is other metadata
                abstract_ps = all_p[1:end_index]
                abstract_raw = ' '.join([str(a_p) for a_p in abstract_ps])

                # Clean abstract
                tokens = word_tokenize(abstract_raw)
                tokens = [t.lower() for t in tokens if len(t) > 1 and t[0].isalpha()]
                tokens = set(tokens)
                tokens = [t for t in tokens if t not in STOPWORDS]

                res[publication] = tokens


if __name__ == '__main__':
    main()
