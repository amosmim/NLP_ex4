from sys import argv
from eval import annon_to_dict as extractor
from collections import defaultdict, Counter

import spacy


nlp = spacy.load('en_core_web_sm')

def find_ent(sent , word):
    for ent in sent.ents:
        if ent.text == word:
            return ent
    return None

def find_head(token):
    leng =0
    head = token.root.head
    while head.head.text != head.text:
        leng += 1
        head = head.head
    return leng, head

def find_first_link_head(token , token2):
    leng, head = find_head(token)
    leng2, head2 = find_head(token2)
    if (head.text != head2.text):
        return 'None'
    dif = leng - leng2
    if dif > 0:
        long = head
        short = head2
    else:
        long = head2
        short = head
    for i in range(1, dif):
        long = long.head
    while (long.text != short.text):
        long = long.head
        short = short.head
    return long.lemma_

if __name__ == '__main__':
    annotation_file_name = argv[1]
    processed_file_name = argv[2]
    dont_care, annotation_data = extractor(annotation_file_name)
    obj1 = defaultdict(Counter)
    obj2 = defaultdict(Counter)
    link = defaultdict(Counter)
    with open(processed_file_name, "r") as f:
        corpus = f.readlines()
        i = 0
        while i < len(corpus)-1:
            if corpus[i][:9] == "#id: sent":
                sent_num = int(corpus[i][9:])
                if sent_num in annotation_data.keys():

                    obj1Targets = set()
                    obj2Targets = set()

                    i += 1 # skip on '#text:' line
                    sent = nlp(unicode(corpus[i][7:]))
                    for relation in annotation_data[sent_num]:
                        obj1Targets.add(relation[0])
                        obj2Targets.add(relation[1])
                        ent = find_ent(sent, relation[0])
                        ent2 = find_ent(sent, relation[1])
                        if ent is not None and ent2 is not None:
                            link['head'][find_first_link_head(ent,ent2)] +=1
                    for ent in sent.ents:
                        if ent.text in obj1Targets:
                            obj1['entities num type'][ent.root.ent_type] +=1
                            obj1['entities type'][ent.label_] +=1
                            #obj1['head'][find_head(ent).lemma_.strip()] += 1
                        if ent.text in obj2Targets:
                            obj2['entities type from root'][ent.root.ent_type] +=1
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
            for type , count in  sorted(ls.items()):
                out.write("\t\t" + str(type) + "="+ str(count) +"\n")
            out.write("\n")
        out.write("\n\nObject 2:\n")
        for field, ls in sorted(obj2.items()):
            out.write("\t" +field + "\n")
            for type, count  in  sorted(ls.items()):
                out.write("\t\t" + str(type) + "="+ str(count) +"\n")
            out.write("\n")

        out.write("\n\nlink:\n")
        for field, ls in sorted(link.items()):
            out.write("\t" + field + "\n")
            for type, count in sorted(ls.items()):
                out.write("\t\t" + str(type) + "=" + str(count) + "\n")
            out.write("\n")
        out.close()
        #print ("obj 1 : " + str(obj1))
        #print ("obj 2 : " + str(obj2))

