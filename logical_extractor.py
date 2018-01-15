from data_handler import DataHandler
import utils
import spacy
from wiki_checker import WikipediaChecker as w_checker

nlp = spacy.load('en')


class LogicalExtractor(object):
    def __init__(self, train_file_path):
        self._dh = DataHandler(train_file_path)
        self.RELATION = 'Live_In'
        self._obj1_options = [u'PERSON']
        self._obj2_options = [u'ORG', u'GPE', u'NORP', u'LOC']

    def _extract_with_ner(self, line):
        sent = nlp(line)
        obj1_list, obj2_list = [], []
        for ne in sent.ents:
            ent_type = ne.root.ent_type_
            if ent_type in self._obj1_options:
                obj1_list.append(ne)
                line = line.replace(ne.text, '$', 1)
            elif ent_type in self._obj2_options:
                obj2_list.append(ne)
                line = line.replace(ne.text, '$', 1)
        return line, obj1_list, obj2_list

    def _extract_with_wiki(self, line, extract_func, ignore_tag='$'):
        wiki_candidates = extract_func(line, window=2)
        line_copy = line
        for candidate in wiki_candidates:
            line_copy = line_copy.replace(candidate, ignore_tag, 1)
        wiki_candidates.extend(extract_func(line_copy, window=1))
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
            wiki_cand_obj1 = self._extract_with_wiki(filtered_line, w_checker.extract_obj1_candidates)
            wiki_cand_obj2 = self._extract_with_wiki(filtered_line, w_checker.extract_obj2_candidates)

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
            for ne1 in obj1_list:
                for ne2 in obj2_list:
                    out_file.write(sent_id + '\t' +
                                   str(ne1) + '\t' + self.RELATION + '\t' + str(ne2) +
                                   '\t( ' + line + ')\n')
        out_file.close()
