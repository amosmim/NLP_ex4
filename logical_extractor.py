from time import time
from data_handler import DataHandler
import utils
import spacy
from wiki_checker import WikipediaChecker as wikiChecker

nlp = spacy.load('en')


class LogicalExtractor(object):
    def __init__(self, train_file_path):
        self._dh = DataHandler(train_file_path)
        self.RELATION = 'Live_In'
        self._obj1_options = [u'PERSON']
        self._obj2_options = [u'ORG', u'GPE', u'NORP', u'LOC']

    def _extract_with_ner(self, line, replacement='$'):
        """ extract candidates using NER-tags by spacy """
        sent = nlp(line)
        obj1_list, obj2_list = [], []
        for ne in sent.ents:
            ent_type = ne.root.ent_type_
            if ent_type in self._obj1_options:
                obj1_list.append(ne.text)
                line = line.replace(ne.text, replacement, 1)
            elif ent_type in self._obj2_options:
                obj2_list.append(ne.text)
                line = line.replace(ne.text, replacement, 1)
        return line, obj1_list, obj2_list

    def _extract_with_wiki(self, line, extract_func, ignore_tag='$'):
        """ extract candidates using wikipedia """
        wiki_candidates = extract_func(line, 2, self._dh)
        line_copy = line
        for candidate in wiki_candidates:
            line_copy = line_copy.replace(candidate, ignore_tag, 1)
        wiki_candidates.extend(extract_func(line_copy, 1, self._dh))
        return wiki_candidates

    def extract(self, in_filename, out_filename):
        """
        goes through filename and write all the relations found,
        correspond to the relation mentioned on top,
        into out_filename
        """
        out_file = open(out_filename, 'w')
        for sent_id, line in utils.read_lines(in_filename):
            # first step - NER
            filtered_line, obj1_list, obj2_list = self._extract_with_ner(line)

            # second step - wikipedia
            wiki_cand_obj1, wiki_cand_obj2 = wikiChecker.extract_with_wiki(self._dh, filtered_line)
            obj1_list.extend(wiki_cand_obj1)
            obj2_list.extend(wiki_cand_obj2)

            # third step - filter the candidates of obj2
            for phrase in list(obj2_list):
                if self._dh.check_cand_obj2(phrase) < 0:
                    obj2_list.remove(phrase)

            # fourth step - update data-handler structures, the given lists supposed to be reliables
            self._dh.add_obj1_cand(obj1_list)
            self._dh.add_obj2_cand(obj2_list)

            # fifth step - match objects to a relation
            for cand1 in obj1_list:
                for cand2 in obj2_list:
                    out_file.write(sent_id + '\t' +
                                   str(cand1) + '\t' + self.RELATION + '\t' + str(cand2) +
                                   '\t( ' + line + ')\n')
        out_file.close()


if __name__ == '__main__':
    t = time()
    print 'start'

    logical_extractor = LogicalExtractor('data/TRAIN.annotations')
    logical_extractor.extract('data/Corpus.DEV.txt', 'output.dev.txt')

    print 'time to run all:', time() - t
