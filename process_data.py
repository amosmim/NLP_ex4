from sys import argv
from eval import annon_to_dict as extractor
from collections import defaultdict, Counter

import spacy


nlp = spacy.load('en_core_web_sm')

if __name__ == '__main__':
    annotation_file_name = argv[1]
    processed_file_name = argv[2]
    dont_care, annotation_data = extractor(annotation_file_name)
    obj1 = defaultdict(Counter)
    obj2 = defaultdict(Counter)
    with open(processed_file_name, "r") as f:
        corpus = f.readlines()
        i = 0
        while i < len(corpus)-1:
            if corpus[i][:9] == "#id: sent":
                sent_num = int(corpus[i][9:])
                if sent_num in annotation_data.keys():
                    obj1Targets = set()
                    obj2Targets = set()
                    for relation in annotation_data[sent_num]:
                        obj1Targets.add(relation[0])
                        obj2Targets.add(relation[1])
                    i += 1 # skip on '#text:' line
                    sent = nlp(unicode(corpus[i][7:]))
                    for ent in sent.ents:
                        if ent.text in obj1Targets:
                            obj1['entities type'][ent.label_] +=1
                        if ent.text in obj2Targets:
                            obj2['entities type'][ent.label_] +=1

                    i += 1
                    while corpus[i] != '\n':
                        parts = corpus[i].split('\t')
                        for target in obj1Targets:
                            if parts[1] in target.split():
                                obj1['field 3'][parts[3]] +=1
                                obj1['field 4'][parts[4]] +=1
                                obj1['field 6'][parts[6]] +=1
                                obj1['field 7'][parts[7]] +=1
                                obj1['field 8'][parts[8].strip()] +=1
                                if parts[8].strip() == '':
                                    print "Null 8 field: " + target + " => "+ str(parts)

                        for target in obj2Targets:
                            if parts[1] in target.split():
                                obj2['field 3'][parts[3]] +=1
                                obj2['field 4'][parts[4]] +=1
                                obj2['field 6'][parts[6]] +=1
                                obj2['field 7'][parts[7]] +=1
                                obj2['field 8'][parts[8].strip()] +=1
                                if parts[8].strip() == '':
                                    print "Null 8 field: "+ target + " => "+ str(parts)
                                elif parts[8] == "PERSON":
                                    print "PERSON in obj2: " + target + " => " + str(parts)
                        i += 1
            i += 1
            f.close()


        out = open("Distribution_of_objects.txt","w")
        out.write("Object 1:\n")
        for field, ls in sorted(obj1.items()):
            out.write("\t" +field + "\n")
            for type , count in  ls.items():
                out.write("\t\t" + type + "="+ str(count) +"\n")
            out.write("\n")
        out.write("\n\nObject 2:\n")
        for field, ls in sorted(obj2.items()):
            out.write("\t" +field + "\n")
            for type, count  in  ls.items():
                out.write("\t\t" + type + "="+ str(count) +"\n")
            out.write("\n")
        out.close()
        #print ("obj 1 : " + str(obj1))
        #print ("obj 2 : " + str(obj2))

