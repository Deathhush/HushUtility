import operator
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
    wordInfo = WordInfo()
    try:
        features = m.feature.decode("utf8").split(",") 
        wordInfo.value = m.surface.decode("utf8")  
        wordInfo.word_class = features[0]
        if (len(features)>6):
            wordInfo.dictionary_form = features[6]
            if wordInfo.dictionary_form == "*":
                return None
        if (len(features)>7):
            wordInfo.spelling = features[7]
        wordInfo.features=features
    except UnicodeDecodeError:
        return None
    return wordInfo

# 中英文双语字幕，一行日文，一行中文
def parse_jpn_cn_subtitle(path, word_dict, skip_bytes=0):
    #for i in itertools.islice(parse_srt(path, 'GB18030'), 69, 70):
    tagger = MeCab.Tagger("")
    for i in parse_srt(path, 'GB18030', skip_bytes):
        if len(i.text) == 2:
            m = tagger.parseToNode(i.text[0].encode("utf-8"))
            while m:
                if m.feature !="BOS/EOS":             
                    word = PopulateWordInfo(m)
                    if word is not None:                        
                        word_key = (word.dictionary_form, word.value)
                        if word_key in word_id_dict:
                            word_dict[word_key] = word_dict[word_key] + 1
                        else:                        
                            word_id_dict[word_key] = str(uuid.uuid1())
                            word_dict[word_key] = 1
                m = m.next

# 纯日文字幕
def parse_pure_jpn_subtitle(path, word_dict, encoding="utf8", skip_bytes=1):
    #for i in itertools.islice(parse_srt(path, 'GB18030'), 69, 70):
    tagger = MeCab.Tagger("")
    for i in parse_srt(path, encoding, skip_bytes):
        for t in i.text:
            m = tagger.parseToNode(t.encode("utf-8"))
            while m:
                if m.feature !="BOS/EOS":             
                    word = PopulateWordInfo(m)
                    if word is not None:
                        word_key = (word.dictionary_form, word.value)
                        if word_key in word_id_dict:
                            word_dict[word_key] = word_dict[word_key] + 1
                        else:                        
                            word_id_dict[word_key] = str(uuid.uuid1())
                            word_dict[word_key] = 1
                m = m.next

def print_word_dict(word_dict, min_count=1):    
    print len(word_dict)
    sorted_x = sorted(word_dict.items(), key=operator.itemgetter(1), reverse=True)
    total = 0
    valid = 0
    for x in sorted_x:
        if (x[1]>=min_count):
            total = total + x[1]
            valid = valid+1
            if type(x[0]) is not tuple:
                print u"{0},{1}".format(x[0], x[1])
            else:
                print u"({0},{1}) {2}".format(x[0][0], x[0][1], x[1])
    print total
    print valid 