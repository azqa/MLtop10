# git clone https://github.com/zelandiya/RAKE-tutorial
import rake
import operator

STOPPATH = 'SmartStoplist.txt'


def get_keywords_of_single_abstract(abstract):
    sentence_list = rake.split_sentences(abstract)
    stopword_pattern = rake.build_stop_word_regex(STOPPATH)
    phrase_list = rake.generate_candidate_keywords(sentence_list, stopword_pattern)
    word_scores = rake.calculate_word_scores(phrase_list)
    keyword_candidates = rake.generate_candidate_keyword_scores(phrase_list, word_scores)
    sorted_keywords = sorted(keyword_candidates.iteritems(), key=operator.itemgetter(1), reverse=True)
    total_keywords = len(sorted_keywords)
    return [k[0] for k in sorted_keywords[0:total_keywords / 3]]
