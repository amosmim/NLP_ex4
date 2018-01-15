from StringIO import StringIO
from time import time
import wikipedia as wiki
import spacy

nlp = spacy.load('en')

obj1_options = [u'PERSON']
obj2_options = [u'ORG', u'GPE', u'NORP', u'LOC']


class WikipediaChecker(object):
    def __init__(self):
        pass

    @staticmethod
    def search_in_wiki(phrase, key_words, valid_types, num_res=3):
        """
        search the given phrase in wikipedia, with one of key-words or one of valid-tags,
        key_words - words to look at the title of search-results,
        valid_types - valid NER tags for the phrase.
        return true if found the phrase with key-word or valid-tag, false otherwise.
        """
        results = wiki.search(phrase, results=num_res)

        # check if any of the search-results contain a key-word
        for search_result in results:
            search_result = search_result.lower()
            for key_word in key_words:
                if key_word in search_result:
                    return True
        # check the summary
        for search_result in results:
            try:
                summary = wiki.summary(search_result, sentences=1)  # check according to the first sentence
                for ne in nlp(summary).ents:
                    if ne.text == phrase and ne.root.ent_type_ in valid_types:
                        return True
            except:
                pass

        return False

    @staticmethod
    def _extract_optional_candidates(line, ignore_str, len_limit):
        cands = []
        line = line.split()
        line = [(i, word) for i, word in enumerate(line) if word.istitle()]

        line_len = len(line)
        for i in range(line_len):
            word_index, word = line[i]
            if word == ignore_str or len(word) < len_limit:
                continue

            curr_phrase = StringIO()
            curr_phrase.write(word)

            j = i
            while j + 1 < line_len and line[j + 1][0] - 1 == word_index:
                curr_phrase.write(' ' + line[j + 1][1])
                line[j + 1] = (-1, ignore_str)
                j += 1
            cands.append(curr_phrase.getvalue())
        return cands

    @staticmethod
    def extract_with_wiki(dh, line, ignore_str='$', len_limit=3):
        obj1_cand, obj2_cand = [], []
        cands = WikipediaChecker._extract_optional_candidates(line, ignore_str, len_limit)
        obj1_key_words = ['name']
        obj2_key_words = ['city', 'state', 'country']

        for phrase in cands:
            obj1_score = dh.check_cand_obj1(phrase)
            if obj1_score > 0:
                obj1_cand.append(phrase)
                continue
            obj2_score = dh.check_cand_obj2(phrase)
            if obj2_score > 0:
                obj1_cand.append(phrase)
                continue
            if obj2_score < 0:
                continue
            if WikipediaChecker.search_in_wiki(phrase, obj1_key_words, obj1_options):
                obj1_cand.append(phrase)
            elif WikipediaChecker.search_in_wiki(phrase, obj2_key_words, obj2_options):
                obj2_cand.append(phrase)

        return obj1_cand, obj2_cand

    @staticmethod
    def extract_obj1_candidates(line, window, dh, ignore_str='$', len_limit=3):
        """ extract words for obj1 in the given line according to the given window """
        line = line.split()
        candidates = []

        for i in range(len(line) - window + 1):
            phrase = ' '.join(line[i:i + window])
            if len(phrase) < len_limit or ignore_str in phrase or not phrase.istitle():
                continue
            if dh.check_cand_obj1(phrase) > 0:
                candidates.append(phrase)
            elif WikipediaChecker.search_in_wiki(phrase, ['name'], obj1_options):
                candidates.append(phrase)

        return candidates

    @staticmethod
    def extract_obj2_candidates(line, window, dh, ignore_str='$', len_limit=3):
        """ extract words for obj2 in the given line according to the given window """
        key_words = ['city', 'state', 'country']
        line = line.split()
        candidates = []

        for i in range(len(line) - window + 1):
            phrase = ' '.join(line[i:i + window])
            if len(phrase) < len_limit or ignore_str in phrase \
                    or dh.check_cand_obj2(phrase) < 0 or not phrase.istitle():
                continue
            if dh.check_cand_obj2(phrase) > 0:
                candidates.append(phrase)
            elif WikipediaChecker.search_in_wiki(phrase, key_words, obj2_options):
                candidates.append(phrase)

        return candidates


if __name__ == '__main__':
    t = time()
    print 'start'

    WikipediaChecker.extract_with_wiki('An enraged Nikita Khrushchev instructed Soviet ships to ignore President'
                                       ' Kennedy \'s naval blockade during the Cuban missile crisis , but the order was'
                                       ' reversed just hours before an inevitable confrontation ,'
                                       ' according to a new book .')

    print 'time to run all:', time() - t
