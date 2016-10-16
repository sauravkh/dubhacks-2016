from api_key import API_KEY
import spacy
import spacy.parts_of_speech as POS
import requests

#Contains the relative frequency of all the words in a corpus, with the most frequently used word ranked "1"
ranks = load_ranks()

#The "reading level", or relative frequency we use to establish whether a word is "difficult"
relative_hard = 10000

#English model for
en_nlp = spacy.load('en')
word_endpoint = 'https://wordsapiv1.p.mashape.com/words/'
word_headers = {
  'X-Mashape-Key': API_KEY,
  'Accept': 'application/json',
}

pos_map = {
  'NOUN': 'noun',
  'ADJ': 'adjective',
  'ADV': 'adverb',
  'VERB': 'verb',
}

def transform(doc_str):
  tups = tokenize(doc_str)
  return [translate(x) if is_hard(x) else x[0] for x in tups]

def translate(tup):
  syns = get_syn(tup)
  if len(syns) == 0:
    return tup[0]
  syns_with_scores = [(get_score(syn), syn) for syn in syns]
  best = min(syns_with_scores)[1]
  return best

def tokenize(doc_str):
  doc = en_nlp(doc_str)
  return [(x.orth_, x.lemma_, pos_map.get(x.pos_, 'other')) for x in doc]

def get_syn(tup):
  (word, lemma, pos) = tup

  res = requests.get(word_endpoint + lemma, headers=word_headers).json()
  syns = parse_syn(res, pos)
  return syns

def parse_syn(res, pos):
  res = res['results']
  for item in res:
    if item['partOfSpeech'] == pos:
      return item['synonyms']
  return []

def is_hard(tup):
  if len(tup[0]) < 3:
    return False
  return get_score(tup[0]) > relative_hard

def get_score(tup):
  return rank[tup[0]]

def load_ranks():
    corpus = open("word_order.csv").readlines()
    print corpus[0:10]
    rank = {}

    for line in corpus:
        line = line.split(",")
        ranks[line[0]] = int(line[1][1:-1])

    return rank
## UNIT TESTS

def test():
  print tokenize(u"Merry has a little sheep")
  print get_syn(('unhinged', 'unhinged', 'adjective'))
  print translate(('unhinged', 'unhinged', 'adjective'))
  print transform(u"Exhausted from reading, I closed my door and got in bed.")
  print is_hard((u'transpirating',))
  print is_hard((u'the',))
  print get_score((u'the',))

if __name__ == '__main__':
  test()