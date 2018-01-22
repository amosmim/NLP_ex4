from StringIO import StringIO
import wikipedia as wiki
import spacy

nlp = spacy.load('en')

obj1_options = [u'PERSON']
obj2_options = [u'ORG', u'GPE', u'NORP', u'LOC']


class WikipediaChecker(object):
    def __init__(self):
        pass

    @staticmethod
    def search_in_wiki(phrase, key_words, valid_types):
        """
        search the given phrase in wikipedia, with one of key-words or one of valid-tags,
        key_words - words to look at the title of search-results,
        valid_types - valid NER tags for the phrase.
        return true if found the phrase with key-word or valid-tag, false otherwise.
        """
        results = wiki.search(phrase)

        for search_result in results:
            # check if any of the search-results contain a key-word
            for key_word in key_words:
                if key_word in search_result:
                    return True
            # check the NER tags
            for ne in nlp(search_result).ents:
                if ne.root.ent_type_ in valid_types:
                    return True
        return False

    @staticmethod
    def _extract_optional_candidates(line, ignore_str, len_limit):
        """ get a list of optional candidates for wiki-check """
        # only titled words
        line = line.split()
        line = [(i, word) for i, word in enumerate(line) if word.istitle()]

        cands = []
        line_len = len(line)
        for i in range(line_len):
            word_index, word = line[i]
            # continue to next if the word needed to be ignored
            if word == ignore_str or len(word) < len_limit:
                continue

            curr_phrase = StringIO()
            curr_phrase.write(word)

            # greedy - get the longest titled phrase
            j = i
            while j + 1 < line_len and line[j + 1][0] - 1 == word_index:
                curr_phrase.write(' ' + line[j + 1][1])
                line[j + 1] = (-1, ignore_str)
                j += 1
            cands.append(curr_phrase.getvalue())
        return cands

    @staticmethod
    def extract_with_wiki(dh, line, ignore_str='$', len_limit=3):
        """ get two lists, each will contain a candidates of the appropriate object in the relation """
        cands = WikipediaChecker._extract_optional_candidates(line, ignore_str, len_limit)

        obj1_cand, obj2_cand = [], []
        obj1_key_words = ['name']
        obj2_key_words = ['city', 'state', 'country']

        for phrase in cands:
            # check if the phrase appeared before and it is a good candidate
            if phrase in obj1_cand:
                obj1_cand.append(phrase)
                continue
            elif phrase in obj2_cand:
                obj2_cand.append(phrase)
                continue

            # obj1 candidate - check by data-handler
            obj1_score = dh.check_cand_obj1(phrase)
            if obj1_score > 0:  # reliable phrase, take it as candidate
                obj1_cand.append(phrase)
                continue

            # obj2 candidate - check by data-handler
            obj2_score = dh.check_cand_obj2(phrase)
            if obj2_score > 0:  # reliable phrase, take it as candidate
                obj1_cand.append(phrase)
                continue
            if obj2_score < 0:  # bad phrase, ignore it
                continue

            # unknown phrase - check in wikipedia
            if WikipediaChecker.search_in_wiki(phrase, obj1_key_words, obj1_options):
                obj1_cand.append(phrase)
            elif WikipediaChecker.search_in_wiki(phrase, obj2_key_words, obj2_options):
                obj2_cand.append(phrase)

        return obj1_cand, obj2_cand
