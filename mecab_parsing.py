import operator
import itertools
import MeCab

class WordInfo(object):
    def __init__(self):
        dictionary_form = ""
        word_class = ""               
        spelling = ""
        value = ""
        features = []
    def __str__(self):
        return "{0},{1},{2},{3}".format(self.value, self.spelling, self.dictionary_form, self.word_class)

def PopulateWordInfo(m):
    features = m.feature.split(",")    
    wordInfo = WordInfo()
    wordInfo.value = m.surface    
    wordInfo.word_class = features[0]
    if (len(features)>6):
        wordInfo.dictionary_form = features[6]
    if (len(features)>7):
        wordInfo.spelling = features[7]
    wordInfo.features=features
    return wordInfo

def parse_file(path, word_dict):
    #for i in itertools.islice(parse_srt(path, 'GB18030'), 69, 70):
    for i in parse_srt(path, 'GB18030'):
        if len(i.text) == 2:
            m = tagger.parseToNode(i.text[0].encode("utf-8"))
            while m:
                if m.feature !="BOS/EOS":             
                    word = PopulateWordInfo(m)
                    if word.dictionary_form in word_dict:
                        word_dict[word.dictionary_form] = word_dict[word.dictionary_form] +1
                    else:
                        word_dict[word.dictionary_form] = 1
                m = m.next

def print_word_dict(word_dict):    
    print len(word_dict)
    sorted_x = sorted(word_dict.items(), key=operator.itemgetter(1), reverse=True)
    total = 0
    valid = 0
    for x in sorted_x:
        total = total + x[1]
        if (x[1]>1):
            valid = valid+1
        print "{0},{1}".format(x[0], x[1])

    print total
    print valid  