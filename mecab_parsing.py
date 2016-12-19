import operator
import MeCab
import uuid
import contextlib
import pypyodbc

@contextlib.contextmanager
def odbc_connect(conn_str):
  conn = pypyodbc.connect(conn_str)
  try:
    yield conn
  finally:
    conn.close()
    
class NoDbWordDbMgr(object):
    def __init__(self):
        return
    def connect(self):
        return
    def clear_db(self):
        return
    def commit(self):
        return
    def insert_file(self, file_name):
        return str(uuid.uuid4())
    def insert_srt_item(self, srt_item, file_id):
        return str(uuid.uuid4())
    def insert_word(self, dict_form, exact_form, word_count):
        return
    def insert_word_item_mapping(self, word_id, item_id):
        return 
    
class WordDbMgr(object):
    def __init__(self, connStr):
        self.conn_str = connStr
    
    def connect(self):
        self._conn = pypyodbc.connect(self.conn_str)
        
    def commit(self):
        if self._conn is not None:
            self._conn.commit()
    
    def close(self):
        if self._conn is not None:
            self._conn.close()    
        
    def insert_file(self, file_name):         
        file_id = str(uuid.uuid4())
        query = "insert into files values(?, ?)"
        self._execute_query(query, (file_id, file_name))
        return file_id
        
    def insert_srt_item(self, srt_item, file_id):
        item_id = str(uuid.uuid4())
        query = "insert into srt_items values(?, ?, ?, ?, ?, ?)"        
        content = ""
        for t in srt_item.text:
            content = content + t + "\n"
        self._execute_query(query, (item_id, file_id, srt_item.index, content, srt_item.start_time, srt_item.end_time))
        return item_id
        
    def insert_word(self, dict_form, exact_form, word_count):
        word_id = str(uuid.uuid4())
        query = "insert into words values(?, ?, ?, ?)"
        self._execute_query(query, (word_id, dict_form, exact_form, word_count))
        
    def insert_word_item_mapping(self, word_id, item_id):
        query = "insert into word_item_mapping values(?, ?)"
        self._execute_query(query, (word_id, item_id))
    
    def clear_db(self):
        query = "truncate table files;truncate table srt_items;truncate table words;truncate table word_item_mapping"
        self._execute_query_and_commit(query)    
        
    def _execute_query(self, query, parameters=None):
        if self._conn is not None:
            self._conn.cursor().execute(query, parameters)
        else:
            self._execute_query_and_commit(query, parameters)
            
    def _execute_query_and_commit(self, query, parameters=None):
        with odbc_connect(self.conn_str) as conn:
            conn.cursor().execute(query, parameters)
            conn.commit()

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
            if (wordInfo.dictionary_form == u"*" or wordInfo.dictionary_form==u"　"):
                return None
        if (len(features)>7):
            wordInfo.spelling = features[7]
        wordInfo.features=features
    except UnicodeDecodeError:
        return None
    return wordInfo

# 中英文双语字幕，一行日文，一行中文
def parse_jpn_cn_subtitle(path, word_dict):
    #for i in itertools.islice(parse_srt(path, 'GB18030'), 69, 70):
    tagger = MeCab.Tagger("")
    for i in parse_srt(path):
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
def parse_pure_jpn_subtitle(path, word_dict):
    #for i in itertools.islice(parse_srt(path, 'GB18030'), 69, 70):
    tagger = MeCab.Tagger("")
    for i in parse_srt(path):
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
    
# 中英文双语字幕，一行日文，一行中文
def load_jpn_cn_subtitle(wordDbMgr, path, word_dict=dict(), word_id_dict=dict()):
    #for i in itertools.islice(parse_srt(path, 'GB18030'), 69, 70):
    tagger = MeCab.Tagger("")
    file_id = wordDbMgr.insert_file(path)
    for i in parse_srt(path):
        i.text = i.text[0:1]
        process_srt_item(wordDbMgr, i, file_id, tagger, word_dict, word_id_dict)

# 纯日文字幕
def load_pure_jpn_subtitle(wordDbMgr, path, word_dict=dict(), word_id_dict=dict()):
    #for i in itertools.islice(parse_srt(path, 'GB18030'), 69, 70):
    tagger = MeCab.Tagger("")
    file_id = wordDbMgr.insert_file(path)
    for i in parse_srt(path):
        process_srt_item(wordDbMgr, i, file_id, tagger, word_dict, word_id_dict)        

def process_srt_item(wordDbMgr, srt_item, file_id, tagger, word_dict, word_id_dict):
    srt_item_id = wordDbMgr.insert_srt_item(srt_item, file_id)        
    for t in srt_item.text:
        m = tagger.parseToNode(t.encode("utf-8"))
        while m:
            if m.feature !="BOS/EOS":
                word = PopulateWordInfo(m)
                if word is not None:
                    word_key = (word.dictionary_form, word.value)
                    if word_key in word_id_dict:
                        word_dict[word_key] = word_dict[word_key] + 1                        
                    else:                        
                        word_id_dict[word_key] = str(uuid.uuid4())
                        word_dict[word_key] = 1
                        #wordDbMgr.insert_word_item_mapping(word_id_dict[word_key], srt_item_id)
            m = m.next