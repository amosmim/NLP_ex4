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
    def extract_obj1_candidates(line, window, ignore_str='$'):
        """ extract words for obj1 in the given line according to the given window """
        line = line.split()
        candidates = []

        for i in range(len(line) - window + 1):
            phrase = ' '.join(line[i:i + window])
            if len(phrase) < 3 or ignore_str in phrase:
                continue
            if WikipediaChecker.search_in_wiki(phrase, ['name'], obj1_options):
                candidates.append(phrase)

        return candidates

    @staticmethod
    def extract_obj2_candidates(line, window, ignore_str='$'):
        """ extract words for obj2 in the given line according to the given window """
        key_words = ['city', 'state', 'country']
        line = line.split()
        candidates = []

        for i in range(len(line) - window + 1):
            phrase = ' '.join(line[i:i + window])
            if len(phrase) < 3 or ignore_str in phrase:
                continue
            if WikipediaChecker.search_in_wiki(phrase, key_words, obj2_options):
                candidates.append(phrase)

        return candidates
